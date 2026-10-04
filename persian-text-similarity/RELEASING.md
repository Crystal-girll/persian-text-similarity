# Publishing and releasing

The URLs in pyproject.toml are intended destinations, not proof that a remote
repository exists. Confirm repository and package name availability first.

1. Review the source and license; confirm `Crystal-girll` is the desired author.
2. Create an empty public GitHub repository named `persian-text-similarity` under
   your account. Do not add a remote README/license that conflicts with these files.
3. In this directory, run:

   ```sh
   git init
   git symbolic-ref HEAD refs/heads/main
   git add .
   git commit -m "Initial Persian text similarity toolkit"
   git remote add origin https://github.com/Crystal-girll/persian-text-similarity.git
   git push -u origin main
   ```

4. Wait for CI to pass. Check the wheel and source distribution artifacts.
5. Update the changelog to the actual release date; synchronize versions in
   pyproject.toml and src/persian_text_similarity/__init__.py.
6. Commit, tag `v0.1.0`, push the tag, and create a GitHub release with the
   changelog and CI-built distributions. PyPI publication is a separate optional
   step and requires verifying package-name availability and credentials.

For later releases, rerun tests/build checks and use a new version/tag. Never
invent users, download counts, issues, commit history, stars, or contributors.
