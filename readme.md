# ScoreSaber Song Sampler (S3Sampler)
Lives are long. Suddenly, we are faced with unexpected things. Sometimes we need a bunch of panties. Sometimes we need thousand of GPUs. Here is a kind of these things. I just wanted to know a latest ranked song database for... something.  

## Usage
**Probably, you do not need to use it by yourself** because you can check the latest database(ranked song only) from [here](./database/).

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
```python src/scraping.py [-u|--unranked]``` : Sample unranked songs too   
```python src/scraping.py [-i|--interval] number``` : Sampling interval second (minimum is 1.5 sec).  
```python src/scraping.py [-v|--view]``` : Disable headless mode(almost for debugging)  
