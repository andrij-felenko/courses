CREATE OPERATOR CLASS box_gist_ops
    DEFAULT FOR TYPE box USING gist AS
    OPERATOR 1  && (box, box),      -- Перетин фігур
    OPERATOR 2  @> (box, box),      -- Повне вміщення
    OPERATOR 3  <@ (box, box),      -- Вміщено у фігуру
    OPERATOR 4  ~= (box, box),      -- Геометрична рівність
    FUNCTION 1  my_gist_consistent(internal, box, smallint, oid, internal),
    FUNCTION 2  my_gist_union(internal, internal),
    FUNCTION 3  my_gist_compress(internal),
    FUNCTION 4  my_gist_decompress(internal),
    FUNCTION 5  my_gist_penalty(internal, internal, internal),
    FUNCTION 6  my_gist_picksplit(internal, internal),
    FUNCTION 7  my_gist_equal(box, box, internal);
