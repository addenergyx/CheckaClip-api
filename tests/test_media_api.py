from app import app


def test_images_endpoint():
    with app.test_client() as client:
        response = client.get('/api/v1/images?search_term=cat')
        assert response.status_code == 200
        data = response.json
        assert len(data['urls']) == 3
        assert all(isinstance(url, str) for url in data['urls'])


def test_invalid_search_term_images_endpoint():
    with app.test_client() as client:
        response = client.get('/api/v1/images?search_term=')
        assert response.status_code == 400
        data = response.json
        assert data == {'errors': {'search_term': 'ensure this value has at least 1 characters'}}


def test_shorts_endpoint():
    with app.test_client() as client:
        response = client.get('/api/v1/shorts?search_term=cat&max_results=5')
        assert response.status_code == 200
        data = response.json
        assert len(data['urls']) == 5
        assert all(url.startswith('https://www.youtube.com/watch?v=') for url in data['urls'])


def test_no_text_shorts_endpoint():
    with app.test_client() as client:
        response = client.get('/api/v1/shorts?search_term=')
        assert response.status_code == 400
        data = response.json
        assert {'search_term': 'String should have at least 1 character'} == data


def test_spaces_shorts_endpoint():
    with app.test_client() as client:
        response = client.get('/api/v1/shorts?search_term=                              ')
        assert response.status_code == 400
        data = response.json
        assert {'search_term': 'String should have at least 1 character'} == data
