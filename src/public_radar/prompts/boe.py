"""BOE prompts for legislation and BORME queries.

Prompts for the Boletín Oficial del Estado (BOE) and
Boletín Oficial del Registro Mercantil (BORME).
"""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

BOE_PROMPTS: dict[str, Prompt] = {
    # =========================================================================
    # Daily Summaries
    # =========================================================================
    "boe_hoy": Prompt(
        name="boe_hoy",
        description="Today's BOE summary with key publications.",
        arguments=[],
    ),
    "boe_por_fecha": Prompt(
        name="boe_por_fecha",
        description="BOE summary for a specific date.",
        arguments=[
            PromptArgument(
                name="fecha",
                description="Date in YYYY-MM-DD format",
                required=True,
            ),
        ],
    ),
    "boe_seccion": Prompt(
        name="boe_seccion",
        description="BOE publications filtered by section.",
        arguments=[
            PromptArgument(
                name="seccion",
                description="Section: 1 (General), 2A (State), 2B (Autonomic), 3 (Other), 4 (Justice), 5 (Ads), T (Court)",
                required=True,
            ),
            PromptArgument(
                name="fecha",
                description="Date (YYYY-MM-DD). Default: today",
                required=False,
            ),
        ],
    ),
    "novedades_legislativas": Prompt(
        name="novedades_legislativas",
        description="Recent legislative news from the last N days.",
        arguments=[
            PromptArgument(
                name="dias",
                description="Number of days to look back (default: 7)",
                required=False,
            ),
            PromptArgument(
                name="tema",
                description="Topic filter (e.g., 'fiscal', 'laboral')",
                required=False,
            ),
        ],
    ),
    # =========================================================================
    # Legislation Search
    # =========================================================================
    "buscar_leyes": Prompt(
        name="buscar_leyes",
        description="Search Spanish laws and regulations by topic.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to search (e.g., 'protección de datos', 'medio ambiente')",
                required=True,
            ),
        ],
    ),
    "buscar_por_rango": Prompt(
        name="buscar_por_rango",
        description="Search legislation by legal type.",
        arguments=[
            PromptArgument(
                name="rango",
                description="Legal type: Ley, Real Decreto, Orden, Real Decreto-ley, etc.",
                required=True,
            ),
            PromptArgument(
                name="tema",
                description="Topic filter (optional)",
                required=False,
            ),
        ],
    ),
    "buscar_por_departamento": Prompt(
        name="buscar_por_departamento",
        description="Search legislation by issuing department/ministry.",
        arguments=[
            PromptArgument(
                name="departamento",
                description="Department name (e.g., 'Hacienda', 'Trabajo')",
                required=True,
            ),
        ],
    ),
    "buscar_por_materia": Prompt(
        name="buscar_por_materia",
        description="Search legislation by subject matter.",
        arguments=[
            PromptArgument(
                name="materia",
                description="Subject matter code or name",
                required=True,
            ),
        ],
    ),
    "legislacion_vigente": Prompt(
        name="legislacion_vigente",
        description="Search only current (non-repealed) legislation.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to search",
                required=True,
            ),
        ],
    ),
    "legislacion_derogada": Prompt(
        name="legislacion_derogada",
        description="Search repealed/historical legislation.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to search",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Law Analysis
    # =========================================================================
    "analizar_ley": Prompt(
        name="analizar_ley",
        description="Complete analysis of a specific law.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID (e.g., BOE-A-2018-16673)",
                required=True,
            ),
        ],
    ),
    "estructura_ley": Prompt(
        name="estructura_ley",
        description="Get the structure/index of a law.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID",
                required=True,
            ),
        ],
    ),
    "articulo_ley": Prompt(
        name="articulo_ley",
        description="Get a specific article from a law.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID",
                required=True,
            ),
            PromptArgument(
                name="articulo",
                description="Article number (e.g., '1', '25')",
                required=True,
            ),
        ],
    ),
    "texto_completo_ley": Prompt(
        name="texto_completo_ley",
        description="Get the full consolidated text of a law.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID",
                required=True,
            ),
        ],
    ),
    "leyes_relacionadas": Prompt(
        name="leyes_relacionadas",
        description="Find laws related to a given legislation.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID",
                required=True,
            ),
            PromptArgument(
                name="tipo_relacion",
                description="Relation type: modifies, modified_by, repeals, repealed_by, references",
                required=False,
            ),
        ],
    ),
    "historial_modificaciones": Prompt(
        name="historial_modificaciones",
        description="Get the modification history of a law.",
        arguments=[
            PromptArgument(
                name="id",
                description="BOE legislation ID",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Auxiliary Tables
    # =========================================================================
    "departamentos_boe": Prompt(
        name="departamentos_boe",
        description="List all government departments with their codes.",
        arguments=[],
    ),
    "rangos_legales": Prompt(
        name="rangos_legales",
        description="List all legal types (Ley, Real Decreto, etc.).",
        arguments=[],
    ),
    "materias_boe": Prompt(
        name="materias_boe",
        description="List all subject matters with their codes.",
        arguments=[],
    ),
    # =========================================================================
    # Specific Topics
    # =========================================================================
    "normativa_fiscal": Prompt(
        name="normativa_fiscal",
        description="Find tax and fiscal legislation.",
        arguments=[
            PromptArgument(
                name="impuesto",
                description="Specific tax (IRPF, IVA, Sociedades, etc.)",
                required=False,
            ),
        ],
    ),
    "normativa_laboral": Prompt(
        name="normativa_laboral",
        description="Find labor and employment legislation.",
        arguments=[
            PromptArgument(
                name="aspecto",
                description="Specific aspect (contratos, despidos, salarios, etc.)",
                required=False,
            ),
        ],
    ),
    "normativa_proteccion_datos": Prompt(
        name="normativa_proteccion_datos",
        description="Find data protection and privacy legislation.",
        arguments=[],
    ),
    "normativa_medioambiental": Prompt(
        name="normativa_medioambiental",
        description="Find environmental legislation.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector (residuos, aguas, emisiones, etc.)",
                required=False,
            ),
        ],
    ),
    "normativa_urbanistica": Prompt(
        name="normativa_urbanistica",
        description="Find urban planning and construction legislation.",
        arguments=[],
    ),
    # =========================================================================
    # BORME (Company Registry)
    # =========================================================================
    "borme_hoy": Prompt(
        name="borme_hoy",
        description="Today's BORME company registry summary.",
        arguments=[],
    ),
    "borme_por_fecha": Prompt(
        name="borme_por_fecha",
        description="BORME summary for a specific date.",
        arguments=[
            PromptArgument(
                name="fecha",
                description="Date in YYYY-MM-DD format",
                required=True,
            ),
        ],
    ),
    "borme_por_provincia": Prompt(
        name="borme_por_provincia",
        description="BORME filtered by province.",
        arguments=[
            PromptArgument(
                name="provincia",
                description="Province name (e.g., 'Madrid', 'Barcelona')",
                required=True,
            ),
            PromptArgument(
                name="fecha",
                description="Date (YYYY-MM-DD). Default: today",
                required=False,
            ),
        ],
    ),
    "constituciones_empresas": Prompt(
        name="constituciones_empresas",
        description="Recently incorporated companies.",
        arguments=[
            PromptArgument(
                name="provincia",
                description="Province filter (optional)",
                required=False,
            ),
        ],
    ),
    "disoluciones_empresas": Prompt(
        name="disoluciones_empresas",
        description="Recently dissolved companies.",
        arguments=[
            PromptArgument(
                name="provincia",
                description="Province filter (optional)",
                required=False,
            ),
        ],
    ),
    "nombramientos_ceses": Prompt(
        name="nombramientos_ceses",
        description="Recent executive appointments and removals.",
        arguments=[
            PromptArgument(
                name="provincia",
                description="Province filter (optional)",
                required=False,
            ),
        ],
    ),
}


def get_boe_prompt_content(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Generate BOE prompt content."""
    args = arguments or {}

    # =========================================================================
    # Daily Summaries
    # =========================================================================
    if name == "boe_hoy":
        return GetPromptResult(
            description="Today's BOE summary",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Dame un resumen del BOE de hoy.

Pasos:
1. Usa get_boe_summary sin parámetros (obtiene el de hoy)
2. Organiza por secciones:
   - Sección 1: Disposiciones generales (leyes, reales decretos)
   - Sección 2A: Autoridades y personal - Estado
   - Sección 2B: Autoridades y personal - CCAA
   - Sección 3: Otras disposiciones
   - Sección 4: Administración de Justicia
   - Sección 5: Anuncios
3. Destaca las publicaciones más importantes
4. Si es fin de semana o festivo, indica que no hay BOE""",
                    ),
                ),
            ],
        )

    elif name == "boe_por_fecha":
        fecha = args.get("fecha", "")
        return GetPromptResult(
            description=f"BOE for {fecha}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Dame el resumen del BOE del día {fecha}.

Pasos:
1. Usa get_boe_summary con date="{fecha}"
2. Organiza las publicaciones por sección
3. Destaca las más relevantes
4. Si no hay publicaciones, indica que ese día no hubo BOE""",
                    ),
                ),
            ],
        )

    elif name == "boe_seccion":
        seccion = args.get("seccion", "1")
        fecha = args.get("fecha")
        fecha_text = f" del {fecha}" if fecha else " de hoy"
        return GetPromptResult(
            description=f"BOE section {seccion}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Dame las publicaciones de la sección {seccion} del BOE{fecha_text}.

Secciones:
- 1: Disposiciones generales
- 2A: Autoridades estatales
- 2B: Autoridades autonómicas
- 3: Otras disposiciones
- 4: Administración de Justicia
- 5: Anuncios
- T: Tribunal Constitucional

Pasos:
1. Usa get_boe_summary con section_filter="{seccion}"
2. Lista todas las publicaciones de esa sección
3. Para cada una muestra título, departamento y enlace""",
                    ),
                ),
            ],
        )

    elif name == "novedades_legislativas":
        dias = args.get("dias", "7")
        tema = args.get("tema")
        tema_text = f" sobre {tema}" if tema else ""
        return GetPromptResult(
            description="Legislative news",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca novedades legislativas de los últimos {dias} días{tema_text}.

Pasos:
1. Usa search_recent_boe con days_back={dias}
2. Filtra por sección 1 (disposiciones generales) principalmente
3. Si hay tema, filtra por términos relacionados con "{tema if tema else ''}"
4. Agrupa por tipo de norma (Ley, RD, Orden)
5. Resume los cambios más importantes""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Legislation Search
    # =========================================================================
    elif name == "buscar_leyes":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Search laws about {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca legislación española sobre: {tema}

Pasos:
1. Usa search_legislation con query="{tema}"
2. Filtra solo legislación vigente (include_derogated=false)
3. Para cada resultado muestra:
   - ID del BOE
   - Título
   - Rango (Ley, RD, etc.)
   - Fecha de publicación
   - Estado de vigencia
4. Ordena por relevancia y fecha
5. Proporciona un resumen del marco normativo""",
                    ),
                ),
            ],
        )

    elif name == "buscar_por_rango":
        rango = args.get("rango", "Ley")
        tema = args.get("tema")
        tema_text = f" sobre {tema}" if tema else ""
        return GetPromptResult(
            description=f"Search {rango}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca normativa de tipo "{rango}"{tema_text}.

Pasos:
1. Usa get_legal_ranges_table para obtener el código del rango
2. Usa search_legislation con legal_range_code correspondiente
3. Lista las normas encontradas con título y fecha
4. Filtra solo las vigentes""",
                    ),
                ),
            ],
        )

    elif name == "buscar_por_departamento":
        departamento = args.get("departamento", "")
        return GetPromptResult(
            description=f"Search by {departamento}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca legislación del departamento/ministerio: {departamento}

Pasos:
1. Usa get_departments_table para encontrar el código del departamento
2. Usa search_legislation con department_code
3. Lista las normas más recientes y relevantes
4. Agrupa por tipo de norma""",
                    ),
                ),
            ],
        )

    elif name == "buscar_por_materia":
        materia = args.get("materia", "")
        return GetPromptResult(
            description=f"Search by matter {materia}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca legislación por materia: {materia}

Pasos:
1. Usa get_matters_table para encontrar el código de la materia
2. Usa search_legislation con matter_code
3. Lista las normas vigentes sobre esta materia
4. Proporciona una visión general del marco regulador""",
                    ),
                ),
            ],
        )

    elif name == "legislacion_vigente":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Current legislation on {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca legislación VIGENTE sobre: {tema}

Pasos:
1. Usa search_legislation con query="{tema}" e include_derogated=false
2. Verifica el estado de consolidación de cada norma
3. Lista solo las que estén en vigor
4. Incluye fecha de última actualización""",
                    ),
                ),
            ],
        )

    elif name == "legislacion_derogada":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Repealed legislation on {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca legislación DEROGADA sobre: {tema}

Pasos:
1. Usa search_legislation con query="{tema}" e include_derogated=true
2. Filtra solo las normas derogadas
3. Indica qué norma la derogó y cuándo
4. Útil para entender la evolución histórica del marco legal""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Law Analysis
    # =========================================================================
    elif name == "analizar_ley":
        ley_id = args.get("id", "")
        return GetPromptResult(
            description=f"Analyze law {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza en detalle la ley: {ley_id}

Pasos:
1. Usa get_legislation_details con legislation_id="{ley_id}" e include_analysis=true
2. Usa get_legislation_structure para ver la estructura
3. Usa find_related_laws para ver relaciones

Proporciona:
- Título y rango normativo
- Fecha de publicación y entrada en vigor
- Departamento que la dicta
- Estructura general (títulos, capítulos)
- Materias que regula
- Leyes que modifica y que la modifican
- Estado de vigencia actual
- Resumen del contenido principal""",
                    ),
                ),
            ],
        )

    elif name == "estructura_ley":
        ley_id = args.get("id", "")
        return GetPromptResult(
            description=f"Law structure {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Muestra la estructura de la ley: {ley_id}

Pasos:
1. Usa get_legislation_structure con legislation_id="{ley_id}"
2. Presenta el índice completo:
   - Títulos y capítulos
   - Artículos (id y título)
   - Disposiciones adicionales
   - Disposiciones transitorias
   - Disposiciones finales
   - Anexos""",
                    ),
                ),
            ],
        )

    elif name == "articulo_ley":
        ley_id = args.get("id", "")
        articulo = args.get("articulo", "1")
        return GetPromptResult(
            description=f"Article {articulo} of {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Dame el artículo {articulo} de la ley {ley_id}.

Pasos:
1. Usa get_legislation_block con legislation_id="{ley_id}" y block_id="a{articulo}"
2. Muestra el texto completo del artículo
3. Si tiene apartados, muéstralos ordenados""",
                    ),
                ),
            ],
        )

    elif name == "texto_completo_ley":
        ley_id = args.get("id", "")
        return GetPromptResult(
            description=f"Full text of {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén el texto completo consolidado de la ley: {ley_id}

Pasos:
1. Usa get_legislation_text con legislation_id="{ley_id}"
2. El texto estará consolidado (con todas las modificaciones incorporadas)
3. Muestra el contenido completo""",
                    ),
                ),
            ],
        )

    elif name == "leyes_relacionadas":
        ley_id = args.get("id", "")
        tipo = args.get("tipo_relacion")
        tipo_text = f" de tipo {tipo}" if tipo else ""
        return GetPromptResult(
            description=f"Related laws to {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca leyes relacionadas con: {ley_id}{tipo_text}

Pasos:
1. Usa find_related_laws con legislation_id="{ley_id}"
2. Muestra las relaciones encontradas:
   - Leyes que modifica
   - Leyes que la modifican
   - Leyes que deroga
   - Leyes que la derogan
   - Referencias cruzadas
3. Explica brevemente cada relación""",
                    ),
                ),
            ],
        )

    elif name == "historial_modificaciones":
        ley_id = args.get("id", "")
        return GetPromptResult(
            description=f"Modification history of {ley_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Muestra el historial de modificaciones de: {ley_id}

Pasos:
1. Usa find_related_laws con legislation_id="{ley_id}" y relation_type="modified_by"
2. Ordena cronológicamente las modificaciones
3. Para cada modificación indica:
   - Qué ley la modifica
   - Fecha de la modificación
   - Artículos afectados (si está disponible)""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Auxiliary Tables
    # =========================================================================
    elif name == "departamentos_boe":
        return GetPromptResult(
            description="List departments",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista todos los departamentos/ministerios con sus códigos.

Pasos:
1. Usa get_departments_table
2. Muestra código y nombre de cada departamento
3. Agrupa por tipo (Ministerios, Organismos, etc.)""",
                    ),
                ),
            ],
        )

    elif name == "rangos_legales":
        return GetPromptResult(
            description="List legal types",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista todos los tipos de normas legales con sus códigos.

Pasos:
1. Usa get_legal_ranges_table
2. Muestra código y nombre de cada rango
3. Explica brevemente la jerarquía normativa:
   - Constitución
   - Leyes Orgánicas
   - Leyes Ordinarias
   - Reales Decretos-ley
   - Reales Decretos
   - Órdenes Ministeriales
   - etc.""",
                    ),
                ),
            ],
        )

    elif name == "materias_boe":
        return GetPromptResult(
            description="List subject matters",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista todas las materias/temas con sus códigos.

Pasos:
1. Usa get_matters_table
2. Muestra código y nombre de cada materia
3. Agrupa por categorías principales""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Specific Topics
    # =========================================================================
    elif name == "normativa_fiscal":
        impuesto = args.get("impuesto")
        impuesto_text = f" específicamente sobre {impuesto}" if impuesto else ""
        return GetPromptResult(
            description="Tax legislation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca normativa fiscal y tributaria{impuesto_text}.

Pasos:
1. Usa search_legislation con query="fiscal tributario impuesto"
2. Filtra por legislación vigente
3. Identifica las normas principales:
   - Ley General Tributaria
   - IRPF
   - IVA
   - Impuesto de Sociedades
   - etc.
4. Muestra las más recientes""",
                    ),
                ),
            ],
        )

    elif name == "normativa_laboral":
        aspecto = args.get("aspecto")
        aspecto_text = f" sobre {aspecto}" if aspecto else ""
        return GetPromptResult(
            description="Labor legislation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca normativa laboral{aspecto_text}.

Pasos:
1. Usa search_legislation con query="laboral trabajo empleo"
2. Filtra por legislación vigente
3. Identifica normas clave:
   - Estatuto de los Trabajadores
   - Ley de Prevención de Riesgos Laborales
   - Convenios colectivos
   - Reforma laboral
4. Muestra las modificaciones más recientes""",
                    ),
                ),
            ],
        )

    elif name == "normativa_proteccion_datos":
        return GetPromptResult(
            description="Data protection legislation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca normativa de protección de datos y privacidad.

Pasos:
1. Usa search_legislation con query="protección datos RGPD LOPD"
2. Identifica las normas principales:
   - LOPDGDD (Ley Orgánica 3/2018)
   - Reglamento GDPR (aplicación)
   - Normativa sectorial
3. Usa get_legislation_details para la LOPDGDD
4. Resume los derechos y obligaciones principales""",
                    ),
                ),
            ],
        )

    elif name == "normativa_medioambiental":
        sector = args.get("sector")
        sector_text = f" en el sector de {sector}" if sector else ""
        return GetPromptResult(
            description="Environmental legislation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca normativa medioambiental{sector_text}.

Pasos:
1. Usa search_legislation con query="medio ambiente ambiental"
2. Incluye normativa sobre:
   - Evaluación ambiental
   - Residuos
   - Aguas
   - Emisiones
   - Espacios protegidos
3. Muestra las normas principales vigentes""",
                    ),
                ),
            ],
        )

    elif name == "normativa_urbanistica":
        return GetPromptResult(
            description="Urban planning legislation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca normativa urbanística y de ordenación del territorio.

Pasos:
1. Usa search_legislation con query="urbanismo suelo edificación"
2. Identifica normas clave:
   - Ley del Suelo
   - Código Técnico de la Edificación
   - Normativa de ordenación territorial
3. Nota: Hay mucha normativa autonómica en esta materia""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # BORME
    # =========================================================================
    elif name == "borme_hoy":
        return GetPromptResult(
            description="Today's BORME",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Dame el resumen del BORME de hoy.

Pasos:
1. Usa get_borme_summary sin parámetros
2. Agrupa los actos por tipo:
   - Constituciones
   - Nombramientos/Ceses
   - Cambios de domicilio
   - Ampliaciones de capital
   - Disoluciones/Liquidaciones
   - Fusiones/Escisiones
3. Muestra estadísticas por provincia
4. Si es fin de semana, indica que no hay BORME""",
                    ),
                ),
            ],
        )

    elif name == "borme_por_fecha":
        fecha = args.get("fecha", "")
        return GetPromptResult(
            description=f"BORME for {fecha}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Dame el resumen del BORME del día {fecha}.

Pasos:
1. Usa get_borme_summary con date="{fecha}"
2. Muestra los actos registrados
3. Agrupa por tipo y provincia""",
                    ),
                ),
            ],
        )

    elif name == "borme_por_provincia":
        provincia = args.get("provincia", "")
        fecha = args.get("fecha")
        fecha_text = f" del {fecha}" if fecha else " de hoy"
        return GetPromptResult(
            description=f"BORME for {provincia}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Dame los actos del BORME{fecha_text} en la provincia de {provincia}.

Pasos:
1. Usa get_borme_summary con province_filter="{provincia}"
2. Lista todos los actos de esa provincia
3. Agrupa por tipo de acto""",
                    ),
                ),
            ],
        )

    elif name == "constituciones_empresas":
        provincia = args.get("provincia")
        provincia_text = f" en {provincia}" if provincia else ""
        return GetPromptResult(
            description="New companies",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca constituciones de empresas recientes{provincia_text}.

Pasos:
1. Usa get_borme_summary con los últimos días
2. Filtra por actos de tipo "Constitución"
3. Muestra:
   - Denominación social
   - Objeto social
   - Capital social
   - Provincia""",
                    ),
                ),
            ],
        )

    elif name == "disoluciones_empresas":
        provincia = args.get("provincia")
        provincia_text = f" en {provincia}" if provincia else ""
        return GetPromptResult(
            description="Company dissolutions",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca disoluciones de empresas recientes{provincia_text}.

Pasos:
1. Usa get_borme_summary
2. Filtra por actos de tipo "Disolución" o "Liquidación"
3. Muestra:
   - Denominación social
   - Causa de disolución
   - Provincia""",
                    ),
                ),
            ],
        )

    elif name == "nombramientos_ceses":
        provincia = args.get("provincia")
        provincia_text = f" en {provincia}" if provincia else ""
        return GetPromptResult(
            description="Appointments and removals",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca nombramientos y ceses recientes{provincia_text}.

Pasos:
1. Usa get_borme_summary
2. Filtra por actos de tipo "Nombramientos" o "Ceses"
3. Muestra:
   - Empresa
   - Cargo
   - Persona
   - Tipo (nombramiento/cese)""",
                    ),
                ),
            ],
        )

    else:
        raise ValueError(f"Unknown BOE prompt: {name}")
