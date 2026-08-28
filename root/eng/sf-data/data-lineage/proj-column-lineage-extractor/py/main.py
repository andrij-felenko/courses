from dataclasses import dataclass, field
from typing import Dict, List, Set
import re

@dataclass
class ColumnDependency:
    target_table: str
    target_column: str
    source_table: str
    source_column: str
    expression_type: str = "DIRECT"

class SimpleSQLLineageExtractor:
    """Екстрактор стовпчикового lineage для запитів із CTE та аліасами."""
    
    def __init__(self):
        self.dependencies: List[ColumnDependency] = []
        self.table_aliases: Dict[str, str] = {}
        self.cte_definitions: Dict[str, str] = {}

    def extract(self, sql_query: str, target_table_name: str) -> List[ColumnDependency]:
        self.dependencies.clear()
        self.table_aliases.clear()
        self.cte_definitions.clear()
        
        # 1. Очищення коментарів та нормалізація пробілів
        clean_sql = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        clean_sql = " ".join(clean_sql.split())
        
        # 2. Виділення CTE: WITH name AS (SELECT ...)
        cte_matches = re.finditer(r'WITH\s+([a-zA-Z_0-9]+)\s+AS\s*\((.*?)\)\s*(SELECT.*)', clean_sql, re.IGNORECASE)
        main_query = clean_sql
        for match in cte_matches:
            cte_name = match.group(1).strip()
            cte_body = match.group(2).strip()
            main_query = match.group(3).strip()
            self.cte_definitions[cte_name] = cte_body

        # 3. Витяг аліасів таблиць з секцій FROM та JOIN
        from_match = re.search(r'FROM\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?', main_query, re.IGNORECASE)
        if from_match:
            real_tbl = from_match.group(1)
            alias = from_match.group(2) or real_tbl
            self.table_aliases[alias] = real_tbl

        join_matches = re.finditer(r'JOIN\s+([a-zA-Z0-9_\.]+)(?:\s+(?:AS\s+)?([a-zA-Z0-9_]+))?', main_query, re.IGNORECASE)
        for jm in join_matches:
            real_tbl = jm.group(1)
            alias = jm.group(2) or real_tbl
            self.table_aliases[alias] = real_tbl

        # 4. Витяг виразів секції SELECT ... FROM
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', main_query, re.IGNORECASE)
        if not select_match:
            return self.dependencies

        select_body = select_match.group(1).strip()
        projections = self._split_projections(select_body)

        for proj in projections:
            self._analyze_projection(proj, target_table_name)

        return self.dependencies

    def _split_projections(self, select_str: str) -> List[str]:
        """Розбиває вирази проекцій з урахуванням вкладених дужок функцій."""
        items = []
        current = []
        depth = 0
        for char in select_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                items.append("".join(current).strip())
                current.clear()
                continue
            current.append(char)
        if current:
            items.append("".join(current).strip())
        return items

    def _analyze_projection(self, proj_expr: str, target_table: str):
        # Визначення імені вихідного стовпця (аліас через AS або пряме ім'я)
        as_match = re.search(r'\s+AS\s+([a-zA-Z0-9_]+)$', proj_expr, re.IGNORECASE)
        if as_match:
            target_col = as_match.group(1)
            expr_body = proj_expr[:as_match.start()].strip()
        else:
            target_col = proj_expr.split('.')[-1].strip()
            expr_body = proj_expr

        # Класифікація типу перетворення
        expr_type = "AGGREGATION" if re.search(r'\b(SUM|AVG|COUNT|MIN|MAX)\b', expr_body, re.IGNORECASE) else "TRANSFORM"
        if re.match(r'^[a-zA-Z0-9_\.]+$', expr_body):
            expr_type = "IDENTITY"

        # Пошук аргументів-стовпців формату alias.column_name
        col_refs = re.finditer(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', expr_body)
        found_sources = False
        for cr in col_refs:
            tbl_alias = cr.group(1)
            src_col = cr.group(2)
            src_table = self.table_aliases.get(tbl_alias, tbl_alias)
            self.dependencies.append(ColumnDependency(
                target_table=target_table,
                target_column=target_col,
                source_table=src_table,
                source_column=src_col,
                expression_type=expr_type
            ))
            found_sources = True

        if not found_sources and '.' not in expr_body:
            first_table = next(iter(self.table_aliases.values())) if self.table_aliases else "unknown"
            self.dependencies.append(ColumnDependency(
                target_table=target_table,
                target_column=target_col,
                source_table=first_table,
                source_column=target_col,
                expression_type=expr_type
            ))

if __name__ == "__main__":
    extractor = SimpleSQLLineageExtractor()
    sql = """
    SELECT
        o.order_id AS order_identifier,
        SUM(o.amount / fx.rate) AS total_revenue_usd,
        o.status
    FROM raw.orders AS o
    JOIN ref.fx_rates AS fx ON o.currency = fx.currency_code
    WHERE o.status = 'COMPLETED'
    """
    
    results = extractor.extract(sql, target_table_name="mart.fct_revenue")
    for dep in results:
        print(f"[{dep.expression_type}] {dep.source_table}.{dep.source_column} -> {dep.target_table}.{dep.target_column}")
