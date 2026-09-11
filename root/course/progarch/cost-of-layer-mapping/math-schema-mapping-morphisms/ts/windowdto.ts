// Схема шару API (тип-добуток з довільними числами)
type WindowDto = {
  width: number;
  height: number;
};

// Інваріант API: формально завжди істинний (приймаємо будь-які вхідні дані)
const pDto = (dto: WindowDto): boolean => true;

// Схема доменного ядра (тип-добуток з інваріантом валідності)
type WindowEntity = {
  width: number;
  height: number;
};

// Інваріант ядра: ширина й висота обов'язково додатні
const pDom = (w: WindowEntity): boolean => w.width > 0 && w.height > 0;

// Наївний мапер: сліпе копіювання полів
const unsafeMap = (dto: WindowDto): WindowEntity => ({
  width: dto.width,
  height: dto.height
});
