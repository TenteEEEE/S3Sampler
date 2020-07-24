MSG="updated: "`date +%Y%m%d`

#git pull
#python src/scraping.py -i 2
git add .
git commit -m "\"${MSG}\""
git push
