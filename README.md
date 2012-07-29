**LogFire** is a modern log collector and viewer, that we have written to use at [3DTin](http://www.3dtin.com)

It uses MongoDB to save the log messages.

Instead of directly writing to MongoDB - which can potentially take long time over network - we write the log messages
to Redis' PubSub channel.

LogFire also comes with an HTTP server that lets you browse log messages saved in the database. Using websockets it also 
allows realtime delivery of log messages to the browser as they get logged on the server.