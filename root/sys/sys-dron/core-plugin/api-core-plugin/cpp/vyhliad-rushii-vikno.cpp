// QGCPalette.h — що саме прилітає в paletteOverride
typedef QColor PaletteColorInfo_t[cMaxTheme][cMaxColorGroup];
//                                 Light|Dark   Disabled|Enabled

// QGCPalette.cc, макрос DECLARE_QGC_COLOR, спрощено до суті:
PaletteColorInfo_t colorInfo = { { QColor(lightDisabled), QColor(lightEnabled) },
                                 { QColor(darkDisabled),  QColor(darkEnabled)  } };
QGCCorePlugin::instance()->paletteOverride(#name, colorInfo);   // тут можна переписати будь-яку клітинку
_colorInfoMap[Light][ColorGroupEnabled][#name] = colorInfo[Light][ColorGroupEnabled];
// …далі всі чотири клітинки лягають у мапу палітри
