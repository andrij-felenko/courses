function totalSize(item: FileSystemItem): number {
  if (item.kind === "file") {
    return item.size;
  } else if (item.kind === "folder") {
    let sum = 0;
    for (const child of item.children) {
      sum += totalSize(child);   // а тут знову той самий if усередині
    }
    return sum;
  }
}
