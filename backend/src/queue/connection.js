const IORedis = require('ioredis');

const redisUrl = process.env.REDIS_URL;

if(!redisUrl) {
    throw new Error('REDIS_URL is not defined in environment variables');
}

const connection  = new IORedis(redisUrl);

module.exports = connection;