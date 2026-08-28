let isScheduled = false;
const updateQueue = new Set<Component>();

export function scheduleUpdate(component: Component) {
  updateQueue.add(component);

  if (!isScheduled) {
    isScheduled = true;
    queueMicrotask(flushUpdates);
  }
}

function flushUpdates() {
  for (const component of updateQueue) {
    component.update();
  }
  updateQueue.clear();
  isScheduled = false;
}
