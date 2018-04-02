const crypto = require("crypto");

const check = (item) => {
    const hash = crypto
        .createHash("sha256")
        .update(item._id + item.time + item.query)
        .digest("hex");

    if (item.hash === undefined) {
        return hash;
    }

    if (item.hash != hash) {
        return false;
    }

    return true;
};

module.exports = check;
