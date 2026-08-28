struct	file
{
	char	f_flag;
	char	f_count;	/* лічильник посилань */
	int	f_inode;	/* покажчик на структуру inode */
	char	*f_offset[2];	/* покажчик читання-запису */
} file[NFILE];

#define	FREAD	01
#define	FWRITE	02
#define	FPIPE	04
