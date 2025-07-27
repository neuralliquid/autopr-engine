import os
from typing import List

import pydantic

from autopr.actions.base import Action


class Inputs(pydantic.BaseModel):
    urls: List[str] = ["/"]
    output_dir: str = "screenshots/gallery"


class Outputs(pydantic.BaseModel):
    success: bool
    screenshot_paths: List[str]


class TakeScreenshots(Action[Inputs, Outputs]):
    """
    [Simulation] Takes screenshots of key pages for a documentation gallery.
    """

    id = "take_screenshots"

    async def run(self, inputs: Inputs) -> Outputs:
        print(f"--- Taking Screenshots ---")
        os.makedirs(inputs.output_dir, exist_ok=True)
        paths = []
        for url in inputs.urls:
            filename = f"{inputs.output_dir}/{url.replace('/', '_')}.png"
            print(f"Taking screenshot of {url} and saving to {filename}")
            paths.append(filename)

        return Outputs(success=True, screenshot_paths=paths)


if __name__ == "__main__":
    import asyncio

    from autopr.tests.utils import run_action_manually

    asyncio.run(
        run_action_manually(
            action=TakeScreenshots,
            inputs=Inputs(urls=["/", "/about"]),
        )
    )
