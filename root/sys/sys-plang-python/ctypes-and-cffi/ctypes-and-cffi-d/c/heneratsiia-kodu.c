/* Фрагмент C-коду, згенерованого CFFI у режимі API */
static PyObject *
_cffi_f_read_sensor(PyObject *self, PyObject *arg0)
{
    SensorData *x0;
    int result;

    /* Пряме отримання нативного покажчика з CData */
    if (_cffi_to_c((char *)&x0, _cffi_type(1), arg0) < 0)
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    result = read_sensor(x0); /* Прямий C-виклик без libffi! */
    Py_END_ALLOW_THREADS

    return _cffi_from_c_int(result, int);
}
