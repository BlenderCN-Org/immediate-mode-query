# immediate-mode-query
Script to query immediate-mode calls in Blender2.8.
See the [Immediate Mode Replacement Task Force](https://wiki.blender.org/index.php/Dev:2.8/Source/OpenGL/Immediate_Mode_Replacement_Tasks link).

Example:
```
$ cd BLENDER_SOURCE_FOLDER
$ cd source/blender
$ query outliner_draw.c
```

Result:
```
Querying file:
./editors/space_outliner/outliner_draw.c

666:    UI_ThemeColorShadeAlpha(TH_BACK, -15, -200);
669:    fdrawline((float)sizex,
674:    fdrawline((float)sizex + OL_RNA_COL_SIZEX,
1654:   UI_ThemeColorShadeAlpha(TH_BACK, -15, -200);
1657:   sdrawline((int)(ar->v2d.cur.xmax - OL_TOG_RESTRICT_VIEWX),
1663:   sdrawline((int)(ar->v2d.cur.xmax - OL_TOG_RESTRICT_SELECTX),
1669:   sdrawline((int)(ar->v2d.cur.xmax - OL_TOG_RESTRICT_RENDERX),
```
