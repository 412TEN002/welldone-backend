#!/bin/bash

echo "Starting database initialization..."

echo "1/3 Adding categories and ingredients..."
python scripts/add_category_and_ingredients.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to add categories and ingredients"
    exit 1
fi

echo "2/3 Adding cooking methods, tools, and heating methods..."
python scripts/add_tool_method_heating.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to add methods and tools"
    exit 1
fi

echo "3/3 Adding cooking settings..."
python scripts/add_cooking_settings.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to add cooking settings"
    exit 1
fi

echo "Database initialization completed successfully!"