import pydantic
import os
from autopr.actions.base import Action

class Inputs(pydantic.BaseModel):
    hook_name: str # e.g., "useTheme"

class Outputs(pydantic.BaseModel):
    created_file: str

HOOK_TEMPLATE = """import {{ useState, useEffect }} from 'react';

export function {name}() {{
  // TODO: Implement hook logic
  const [value, setValue] = useState(null);

  useEffect(() => {{
    // Side effect logic goes here
  }}, []);

  return value;
}}
"""

class ScaffoldSharedHook(Action[Inputs, Outputs]):
    """
    Scaffolds a new React hook file in the shared/hooks directory.
    """
    id = "scaffold_shared_hook"

    async def run(self, inputs: Inputs) -> Outputs:
        hook_dir = "shared/hooks"
        filename = f"{hook_dir}/{inputs.hook_name}.ts"
        
        os.makedirs(hook_dir, exist_ok=True)
        
        content = HOOK_TEMPLATE.format(name=inputs.hook_name)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        return Outputs(created_file=filename)

if __name__ == "__main__":
    from autopr.tests.utils import run_action_manually
    import asyncio
    asyncio.run(
        run_action_manually(
            action=ScaffoldSharedHook,
            inputs=Inputs(hook_name="useNewSharedHook"),
        )
    ) 