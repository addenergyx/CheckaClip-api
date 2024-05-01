from app import convert_to_embed_url

def test_convert_to_embed_url():
    video_url = "https://www.youtube.com/watch?v=11111111"
    assert convert_to_embed_url(video_url) == "https://www.youtube.com/embed/11111111"

