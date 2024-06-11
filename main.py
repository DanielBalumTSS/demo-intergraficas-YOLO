from connectoCCTV import ReadingCamera

#urls = ["rtsp://CCTV:cctv2021@192.168.0.26:554/Streaming/Channels/1"]
urls = ["C:/Users/Daniel/Downloads/output.mp4"]

videoTest = ReadingCamera(urls)
videoTest.startReading()