#!/bin/bash

# This script is used to delete all *.py and *.pyc files within the migrations directories from specified directories,
# except for __init__.py.

# Usage: galandriel.sh -d dir1 [dir2 ...]
#   -d: Specify base directories from which the migration files will be deleted

confirm() {
    echo "You are about to delete all *.py and *.pyc files within the following migrations directories, except for __init__.py:"
    for dir in "$@"; do
        echo "$dir/migrations"
    done
    read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        return 0
    else
        echo "Operation canceled."
        exit 1
    fi
}

delete_migrations() {
    for dir in "$@"; do
        migrations_dir="$dir/migrations"
        if [ -d "$migrations_dir" ]; then
            echo "Deleting *.py and *.pyc files in migrations directory (except for __init__.py): $migrations_dir"
            find "$migrations_dir" -type f \( -name "*.py" -o -name "*.pyc" \) ! -name "__init__.py" -delete
        else
            echo "Migrations directory not found: $migrations_dir"
        fi
    done
}

if [[ "$1" == "-d" ]]; then
    shift # Remove the '-d' argument
    confirm "$@"
    delete_migrations "$@"
else
    echo "Usage: galandriel.sh -d dir1 [dir2 ...]"
    exit 1
fi
