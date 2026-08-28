const API = "https://api.digitalhomes.io";
const get = (p: string) => fetch(API + p).then(r => r.json());

// найгірший, але найчастіший варіант — послідовно, «бо так читається зверху вниз»
async function loadPanelNaive(homeId: number) {
  const home = await get(`/homes/${homeId}`);          // 1
  for (const rid of home.roomIds) {
    const room = await get(`/rooms/${rid}`);            // ×5
    for (const did of room.deviceIds) {
      const dev = await get(`/devices/${did}`);         // ×15
      paint(room, dev);                                 // 21 оберт ПІДРЯД
    }
  }
}
