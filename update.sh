MSG="updated: "`date +%Y%m%d`

git pull
python src/scraping.py
git add .
git commit -m "${MSG}"
git push
