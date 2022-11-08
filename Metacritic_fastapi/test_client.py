import httpx
import time
from statistics import mean
import json

def games_get():
    return (
    'diablo',
    'TeRRaria',
    'stray',
    'Stray?console=playstation-5',
    'vampire survivors?console=xbox-one'
    )
def games_404():
    return (
        'ngnx',
        'diablo?console=playstation-5',
        'vampire survivors?console=opera')

def test_connection():
    with httpx.Client() as client:
        start_time = time.time()
        m=client.get('http://127.0.0.1:8000/')
        assert m.status_code == 200
        mp=client.get('http://127.0.0.1:8000/platforms')
        assert mp.status_code == 200

def test_go_throug_games():
    for game in games_get():
        with httpx.Client() as client:
            print(game)
            m=client.get(f'http://127.0.0.1:8000/games/{game}')
        assert m.status_code == 200

def test_go_404():
    for game in games_404():
        with httpx.Client() as client:
            m=client.get(f'http://127.0.0.1:8000/games/{game}')
        assert m.status_code == 404
        assert 'Game not found' in m.json()['detail']

#time check
if __name__=='__main__': 
    k=[]
    with httpx.Client(timeout=None) as client:
        for i in range(50):
            start_time = time.time()
            m=client.get('http://127.0.0.1:8000/games/TeRRaria')
            k.append (time.time() - start_time)
            print(time.time() - start_time)
    print(mean(k))
