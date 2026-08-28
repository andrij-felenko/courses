   import numpy as np
   import matplotlib.pyplot as plt

   # Завантаження даних
   data = np.genfromtxt('dipole_field_grid.csv', delimiter=',', names=True)
   x = np.unique(data['x'])
   y = np.unique(data['y'])
   X, Y = np.meshgrid(x, y)
   Bx = data['Bx'].reshape(len(x), len(y))
   By = data['By'].reshape(len(x), len(y))
   B_mag = data['B_mag'].reshape(len(x), len(y))

   # Побудова силових ліній у площині XY
   plt.figure(figsize=(8, 6))
   strm = plt.streamplot(X, Y, Bx, By, color=np.log10(B_mag), cmap='inferno', density=1.5)
   plt.colorbar(strm.lines, label='log10(|B| / Tl)')
   plt.title('Магнітне поле системи диполів')
   plt.xlabel('X (м)')
   plt.ylabel('Y (м)')
   plt.grid(True)
   plt.savefig('dipole_streamlines.png', dpi=300)
