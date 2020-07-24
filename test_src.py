import pytest
from src.scraping import scoresaber_scraper


def test_scraper_init():
    try:
        scraper = scoresaber_scraper()
        assert True
    except:
        assert False
    finally:
        scraper.__del__()


def test_scraper_init_with_tooshort_interval():
    try:
        scraper = scoresaber_scraper(interval=0)
        if scraper.interval == 5:
            assert True
        else:
            assert False
    except:
        assert False
    finally:
        scraper.__del__()


def test_scraper_init_with_unranked():
    try:
        scraper = scoresaber_scraper(unranked=True)
        assert True
    except:
        assert False
    finally:
        scraper.__del__()


def test_ranked_scraping():
    try:
        scraper = scoresaber_scraper(interval=2)
        scraper.scrape(range(1))
        assert True
    except:
        assert False
    finally:
        scraper.__del__()


def test_dataframe_conversion():
    try:
        scraper = scoresaber_scraper(interval=2)
        scraper.scrape(range(1))
        songdf = scraper.to_dataframe()
        assert True
    except:
        assert False
    finally:
        scraper.__del__()


def test_unranked_scraping():
    try:
        scraper = scoresaber_scraper(interval=2, unranked=True)
        scraper.scrape(range(1))
        assert True
    except:
        assert False
    finally:
        scraper.__del__()
