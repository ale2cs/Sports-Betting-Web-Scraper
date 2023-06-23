import httpx
import time

from playwright.sync_api import sync_playwright
url = "https://stake.com/sports/baseball/usa/mlb"
game_url = "https://stake.com/sports/baseball/usa/mlb/43585381-philadelphia-phillies-atlanta-braves"
graph_url = "https://stake.com/_api/graphql"

def test_json(resp):
    try:
        print(resp.json())
    except:
        pass

with sync_playwright() as playwright:
    browser = playwright.firefox.launch(headless=False)
    page = browser.new_page()
    context = browser.new_context()
    api_context = context.request
    page.on('request', lambda request: print(request.method, request.url))
    page.on('response', lambda response: test_json(response))
    page.goto(url)
    page.wait_for_timeout(1000)
    time.sleep(5)   
    
    browser.close()
