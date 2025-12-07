import json
import os
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from src.config import settings
from src.models.config_editor import City, Preset
from src.utils.auth import verify_api_key

router = APIRouter(prefix="/config", tags=["Config editor"])


def _load_config() -> dict[str, Any]:
    try:
        with open(settings.CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Config file not found")  # noqa: B904
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid config.json: {e!s}")  # noqa: B904


def _save_config(cfg: dict[str, Any]) -> None:
    try:
        with open(settings.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save config: {e!s}")  # noqa: B904


def _safe_filename(name: str) -> str:
    if "/" in name or "\\" in name or name.startswith(".") or ".." in name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    return name


@router.get("", include_in_schema=False)
async def config_page():
    ui_index = os.path.join("storage", "config-ui", "index.html")
    if not os.path.exists(ui_index):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="UI not found. Please add storage/config-ui/index.html"
        )
    return FileResponse(ui_index, media_type="text/html; charset=utf-8")


# ---------- Raw config ----------
@router.get("/api/config", dependencies=[Depends(verify_api_key)])
async def get_config():
    return _load_config()


# ---------- Cities ----------
@router.get("/api/cities", dependencies=[Depends(verify_api_key)])
async def list_cities():
    cfg = _load_config()
    phones = cfg.get("city2phone", {})
    emails = cfg.get("city2email", {})
    vks = cfg.get("city2vk", {})
    all_cities = set(phones) | set(emails) | set(vks)
    result = []
    for city in sorted(all_cities):
        result.append(
            {
                "name": city,
                "phone": phones.get(city),
                "email": emails.get(city),
                "vk": vks.get(city),
            }
        )
    return {"items": result}


@router.post("/api/cities", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_201_CREATED)
async def add_city(city: City):
    cfg = _load_config()
    cfg.setdefault("city2phone", {})
    cfg.setdefault("city2email", {})
    cfg.setdefault("city2vk", {})
    if city.name in cfg["city2phone"] or city.name in cfg["city2email"] or city.name in cfg["city2vk"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="City already exists")
    cfg["city2phone"][city.name] = city.phone
    cfg["city2email"][city.name] = city.email
    cfg["city2vk"][city.name] = city.vk
    _save_config(cfg)
    return {"ok": True}


@router.put("/api/cities/{name}", dependencies=[Depends(verify_api_key)])
async def update_city(name: str, city: City):
    if name != city.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Renaming is not supported. Delete and add again."
        )
    cfg = _load_config()
    for key in ("city2phone", "city2email", "city2vk"):
        if name not in cfg.get(key, {}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    cfg["city2phone"][name] = city.phone
    cfg["city2email"][name] = city.email
    cfg["city2vk"][name] = city.vk
    _save_config(cfg)
    return {"ok": True}


@router.delete("/api/cities/{name}", dependencies=[Depends(verify_api_key)])
async def delete_city(name: str):
    cfg = _load_config()
    found = False
    for key in ("city2phone", "city2email", "city2vk"):
        if name in cfg.get(key, {}):
            cfg[key].pop(name, None)
            found = True
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    _save_config(cfg)
    return {"ok": True}


# ---------- Fonts ----------
@router.get("/api/fonts", dependencies=[Depends(verify_api_key)])
async def list_fonts():
    folder = settings.FONT_FOLDER
    os.makedirs(folder, exist_ok=True)
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return {"items": sorted(files)}


@router.post("/api/fonts", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_201_CREATED)
async def upload_font(file: UploadFile = File(...)):  # noqa: B008
    filename = _safe_filename(file.filename or "")
    folder = settings.FONT_FOLDER
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, filename)
    try:
        with open(dst, "wb") as out:
            out.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save font: {e!s}")  # noqa: B904
    return {"ok": True, "filename": filename}


@router.delete("/api/fonts/{filename}", dependencies=[Depends(verify_api_key)])
async def delete_font(filename: str):
    filename = _safe_filename(filename)
    path = os.path.join(settings.FONT_FOLDER, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Font not found")
    try:
        os.remove(path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete font: {e!s}")  # noqa: B904
    return {"ok": True}


# ---------- Templates (images) ----------
@router.get("/api/templates", dependencies=[Depends(verify_api_key)])
async def list_templates():
    folder = settings.TEMPLATE_FOLDER
    os.makedirs(folder, exist_ok=True)
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return {"items": sorted(files)}


@router.post("/api/templates", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_201_CREATED)
async def upload_template(file: UploadFile = File(...)):  # noqa: B008
    filename = _safe_filename(file.filename or "")
    folder = settings.TEMPLATE_FOLDER
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, filename)
    try:
        with open(dst, "wb") as out:
            out.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save template: {e!s}")  # noqa: B904
    return {"ok": True, "filename": filename}


@router.delete("/api/templates/{filename}", dependencies=[Depends(verify_api_key)])
async def delete_template(filename: str):
    filename = _safe_filename(filename)
    path = os.path.join(settings.TEMPLATE_FOLDER, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    try:
        os.remove(path)
    except Exception as e:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete template: {e!s}"
        )
    return {"ok": True}


# ---------- Presets ----------
@router.get("/api/presets", dependencies=[Depends(verify_api_key)])
async def list_presets():
    cfg = _load_config()
    return {"items": cfg.get("presets", [])}


@router.post("/api/presets", dependencies=[Depends(verify_api_key)], status_code=status.HTTP_201_CREATED)
async def add_preset(preset: Preset):
    cfg = _load_config()
    presets: list[dict[str, Any]] = cfg.get("presets", [])
    if any(p.get("name") == preset.name for p in presets):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Preset already exists")
    presets.append(preset.model_dump())
    cfg["presets"] = presets
    _save_config(cfg)
    return {"ok": True}


@router.put("/api/presets/{name}", dependencies=[Depends(verify_api_key)])
async def update_preset(name: str, preset: Preset):
    if name != preset.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Renaming is not supported. Delete and add again."
        )
    cfg = _load_config()
    presets: list[dict[str, Any]] = cfg.get("presets", [])
    for idx, p in enumerate(presets):
        if p.get("name") == name:
            presets[idx] = preset.model_dump()
            cfg["presets"] = presets
            _save_config(cfg)
            return {"ok": True}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")


@router.delete("/api/presets/{name}", dependencies=[Depends(verify_api_key)])
async def delete_preset(name: str):
    cfg = _load_config()
    presets: list[dict[str, Any]] = cfg.get("presets", [])
    new_presets = [p for p in presets if p.get("name") != name]
    if len(new_presets) == len(presets):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    cfg["presets"] = new_presets
    _save_config(cfg)
    return {"ok": True}
