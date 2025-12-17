# Pro Tips

Quick tips and tricks learned during development.

---

## Git: Tracking Empty Folders

**Problem:** Git doesn't track empty directories. When you create folder structure, empty folders won't show up in GitHub.

**Solution:** Add `.gitkeep` files to empty directories.

```bash
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch src/.gitkeep
touch notebooks/.gitkeep
touch tests/.gitkeep
```

**Better:** Add this to your project setup script so you never forget:

```bash
# In your create-project script:
mkdir -p data/{raw,processed}
mkdir -p src
mkdir -p notebooks
mkdir -p tests

# Add .gitkeep files automatically
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch src/.gitkeep
touch notebooks/.gitkeep
touch tests/.gitkeep
```

---

## More tips will be added as we progress...
