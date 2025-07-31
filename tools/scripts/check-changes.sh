#!/bin/bash

echo "Changed files in the current commit:"
git show --name-only

echo -e "\nChanges to package.json:"
git show -- package.json
