export default class Stack {
  constructor() {
    this.items = [];
  }
  push(item) {
    this.items.push(item);
  }
  pop() {
    return this.items.pop();
  }
  peek() {
    if (this.items.length > 0) {
      return this.items[this.items.length - 1];
    }
    return null;
  }
  getSize() {
    return this.items.length;
  }
  isEmpty() {
    return this.items.length == 0;
  }
}
