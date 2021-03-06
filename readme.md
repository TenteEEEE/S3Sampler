# ScoreSaber Song Sampler (S3Sampler)
Lives are long. Suddenly, we are faced with unexpected things. Sometimes we need a bunch of panties. Sometimes we need thousand of GPUs. Here is a kind of these things. I just wanted to know a latest ranked song database for... something.  

## Auto-Genned Google Sheets
You can check the data from [ScoreSaberRankedSongDB](https://docs.google.com/spreadsheets/d/1NZpCVfejZgJBtrJL0AukMz4KODm_MKKEPhxN9CR34BE/edit?usp=sharing).  
You have a viewer permission only, but you can sort the data from filtering icon->"Make a temporary filtered view".  
![img](https://user-images.githubusercontent.com/9051681/88448983-39d9d600-ce7e-11ea-80b9-1068d3f518b0.png)

## Twitter Bot (New Ranked Songs Notifier)
See [Ranked Song Bot(@S3Sampler)](https://twitter.com/S3Sampler).  
This bot tweets new ranked songs through [#NewRankedSong](https://twitter.com/search?q=%23NewRankedSong&src=typed_query) tag.

## Usage
**Probably, you do not need to use it by yourself** because you can check the latest database(ranked song only) from [the above sheet](https://docs.google.com/spreadsheets/d/1NZpCVfejZgJBtrJL0AukMz4KODm_MKKEPhxN9CR34BE/edit?usp=sharing) or [here](./database/).

Anyway, when you want to make it by yourself,  
```python src/scraping.py```  
After the scraping, you will get "song_db.json" and "song_db.csv".  
JSON provides minimum information.  
CSV provides a flattened table. It may easy to handle from any applications.

If you want to get a perfect(unranked and ranked) song database,  
```python src/scraping.py -u```  
**I guess it takes about 3~5days if gently sampled.**

## Options
```python src/scraping.py [-h|--help]``` : See the help menu  
```python src/scraping.py [-r|--restart]``` : Restart from temporary files   
```python src/scraping.py [-u|--unranked]``` : Sample unranked songs too   
```python src/scraping.py [-i|--interval] number``` : Sampling interval second (minimum is 1.5 sec).  
```python src/scraping.py [-v|--view]``` : Disable headless mode(almost for debugging)  

## Log
2020/07/31: Support Twitter Notification Bot  
2020/07/29: It prints new songs if it exists  
2020/07/25: Support Beatsaver information sampling  
2020/07/24: Initial commit, and started daily updating
