import json
from datetime import date
from typing import Literal

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/buildings")
async def list_buildiings(
    limit: int = 100,
    order: Literal["asc", "desc"] = "desc",
):
    with (
        open("buildings.json") as buildings_file,
        open("tenders.json") as tenders_file,
    ):
        buildings = json.load(buildings_file)
        tenders = json.load(tenders_file)

    for building in buildings:
        if not building.get("prozorro_tender"):
            continue

        tender_id = building["prozorro_tender"]["id"]
        building["prozorro_tender"] = next(t for t in tenders if t["id"] == tender_id)

    results = sorted(
        buildings,
        key=lambda building: date.fromisoformat(building["date"]),
        reverse=order == "desc",
    )[:limit]
    return results


@app.get("/tenders")
async def list_tenders(
    limit: int = 100,
    order: Literal["asc", "desc"] = "desc",
):
    with open("tenders.json") as tenders_file:
        tenders = json.load(tenders_file)

    results = sorted(tenders, key=lambda t: t["id"], reverse=order == "desc")[:limit]
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
