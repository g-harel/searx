const mongodb = require("mongodb");
const request = require("request-promise");

const check = require("./check");

const url = "mongodb://user123:password123@ds249398.mlab.com:49398/searx";
const dbname = "searx";
const delay = 10 * 1000;

const report = (item) =>
    request({
        method: "POST",
        uri: "http://funapp.pythonanywhere.com/report",
        body: {
            type: "long term consistency check failed",
            date: Date.now().toString(),
            data: JSON.stringify(item)
        },
        json: true
    });

const ensure = async () => {
    const client = await mongodb.MongoClient.connect(url);
    const trending = client.db(dbname).collection("trending");

    const items = await trending.find({}).toArray();
    const changes = [];

    await Promise.all(
        items.map((item) => {
            const hash = check(item);

            // item is consistent
            if (hash === true) {
                return;
            }

            // item is inconsistent
            if (hash === false) {
                changes.push(`hash inconsistency on item with id ${item._id}`);
                return Promise.all(
                    trending.deleteOne({ _id: item._id }),
                    report(item)
                );
            }

            // missing hash is added to the item
            changes.push(`hash added to item with id ${item._id}`);
            return trending.updateOne({ _id: item._id }, { $set: { hash } });
        })
    );

    await client.close();

    return changes;
};

const loop = async () => {
    const changes = await ensure();
    if (changes.length > 0) {
        console.log(changes);
    }
    setTimeout(loop, delay);
};

loop();
