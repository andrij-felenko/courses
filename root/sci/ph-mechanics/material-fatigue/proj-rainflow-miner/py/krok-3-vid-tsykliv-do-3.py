sn = SNCurve(s1=250, n1=1e3, s2=90, n2=1e6, ult=310)
history = [25, 190, 70, 225, 95, 160, 60, 240, 85, 205, 55, 175]

rev = turning_points(history)
closed, residue = rainflow(rev)
D = block_damage(rev, sn)

print("замкнені цикли (амп, серед):")
for amp, mean in closed:
    print(f"   {amp:5.1f}  {mean:5.1f}")
print("залишок:", residue)
print(f"шкода за політ D = {D:.3e}")
print(f"польотів до руйнування = {1/D:,.0f}")
print(f"годин до руйнування    = {1/D * 12/60:,.0f}")
