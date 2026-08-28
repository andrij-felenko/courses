#define __define_initcall(level,fn) \
	static initcall_t __initcall_##fn __attribute_used__ \
	__attribute__((__section__(".initcall" level ".init"))) = fn

#define core_initcall(fn)	__define_initcall("1",fn)
#define postcore_initcall(fn)	__define_initcall("2",fn)
#define arch_initcall(fn)	__define_initcall("3",fn)
#define subsys_initcall(fn)	__define_initcall("4",fn)
#define fs_initcall(fn)		__define_initcall("5",fn)
#define device_initcall(fn)	__define_initcall("6",fn)
#define late_initcall(fn)	__define_initcall("7",fn)
