from app import app # Flask instance of the API
 
def test_index_route():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_time_it_index_route(benchmark):
    benchmark(test_index_route)

def test_upload():

    payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"imagefile\"; filename=\"Large.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"title\"\r\n\r\nTest Image V\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\nHello from insomnia!\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"tags\"\r\n\r\ntest test test\r\n-----011000010111000001101001--\r\n"
    headers = {"Content-Type": "multipart/form-data; boundary=---011000010111000001101001"}

    resp = app.test_client().post('/add', data=payload, headers = headers)

    assert resp.status_code == 302


def test_time_it_upload(benchmark):
    benchmark(test_upload)
# searches based on img name and checks that images are returned

def test_search():
    querystring = "test test test"
    payload = ""
    response = app.test_client().get(f'/search?query={querystring}' ,data=payload)

    assert response.status_code == 200
    assert response.content_length > 0

def test_time_it_search(benchmark):
    benchmark(test_search)