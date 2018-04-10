const check = require("./check");

const item = (hash) => ({
    _id: "id",
    time: "time",
    query: "query",
    hash
});

it("should return a hash if it is not in the item", () => {
    expect(typeof check(item(undefined))).toBe("string");
});

it("should return false when the hash does not match", () => {
    expect(check(item(""))).toBe(false);
});

it("should return true when the hash matches", () => {
    let h = "eec87f74dfcb334945b82b947725845fb16e559e8b09fe180fd35bdf2ff746ca";
    expect(check(item(h))).toBe(true);
});
