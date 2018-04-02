const mongodb = require('mongodb');

const url = 'mongodb://user123:password123@ds249398.mlab.com:49398/searx';
const dbname = 'searx';
const delay = 3 * 1000;

const check = async () => {
    const client = await mongodb.MongoClient.connect(url);
    const trending = client.db(dbname).collection('trending');

    (await trending.find({}).toArray()).map((item) => {
        console.log(item.query);
    });

    await client.close();
};

const loop = async () => {
    await check();
    setTimeout(loop, delay);
}

loop();