from app import app # Flask instance of the API
    
 
def test_index_route():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_time_it(benchmark):
    benchmark(test_index_route)
