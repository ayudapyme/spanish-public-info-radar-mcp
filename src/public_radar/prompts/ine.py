"""INE prompts for statistics queries.

Prompts for the Instituto Nacional de Estadística (INE).
"""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

INE_PROMPTS: dict[str, Prompt] = {
    # =========================================================================
    # General Discovery
    # =========================================================================
    "operaciones_estadisticas": Prompt(
        name="operaciones_estadisticas",
        description="List all available statistical operations from INE.",
        arguments=[],
    ),
    "buscar_estadistica": Prompt(
        name="buscar_estadistica",
        description="Search for statistical operations by topic.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to search (e.g., 'población', 'turismo', 'empleo')",
                required=True,
            ),
        ],
    ),
    "tablas_operacion": Prompt(
        name="tablas_operacion",
        description="List tables available for a specific operation.",
        arguments=[
            PromptArgument(
                name="operacion",
                description="Operation code (e.g., 'IPC', 'EPA', 'PIB')",
                required=True,
            ),
        ],
    ),
    "variables_operacion": Prompt(
        name="variables_operacion",
        description="List variables available for a specific operation.",
        arguments=[
            PromptArgument(
                name="operacion",
                description="Operation code",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Key Economic Indicators
    # =========================================================================
    "ipc_inflacion": Prompt(
        name="ipc_inflacion",
        description="Get Consumer Price Index (CPI) and inflation data.",
        arguments=[
            PromptArgument(
                name="periodos",
                description="Number of periods to retrieve (default: 12)",
                required=False,
            ),
        ],
    ),
    "ipc_por_grupos": Prompt(
        name="ipc_por_grupos",
        description="Get CPI breakdown by product groups.",
        arguments=[],
    ),
    "inflacion_subyacente": Prompt(
        name="inflacion_subyacente",
        description="Get core inflation (excluding energy and fresh food).",
        arguments=[],
    ),
    "pib_trimestral": Prompt(
        name="pib_trimestral",
        description="Get quarterly GDP growth data.",
        arguments=[
            PromptArgument(
                name="periodos",
                description="Number of quarters to retrieve (default: 8)",
                required=False,
            ),
        ],
    ),
    "pib_por_sectores": Prompt(
        name="pib_por_sectores",
        description="Get GDP breakdown by economic sectors.",
        arguments=[],
    ),
    # =========================================================================
    # Employment Statistics
    # =========================================================================
    "epa_paro": Prompt(
        name="epa_paro",
        description="Get unemployment rate from EPA survey.",
        arguments=[
            PromptArgument(
                name="periodos",
                description="Number of quarters to retrieve (default: 8)",
                required=False,
            ),
        ],
    ),
    "epa_ocupados": Prompt(
        name="epa_ocupados",
        description="Get employment figures from EPA survey.",
        arguments=[],
    ),
    "epa_por_sexo": Prompt(
        name="epa_por_sexo",
        description="Get employment data broken down by sex.",
        arguments=[],
    ),
    "epa_por_edad": Prompt(
        name="epa_por_edad",
        description="Get employment data broken down by age groups.",
        arguments=[],
    ),
    "epa_por_comunidad": Prompt(
        name="epa_por_comunidad",
        description="Get employment data by autonomous community.",
        arguments=[],
    ),
    "paro_juvenil": Prompt(
        name="paro_juvenil",
        description="Get youth unemployment rate (under 25).",
        arguments=[],
    ),
    # =========================================================================
    # Demographics
    # =========================================================================
    "poblacion_espana": Prompt(
        name="poblacion_espana",
        description="Get Spain's total population figures.",
        arguments=[],
    ),
    "poblacion_por_ccaa": Prompt(
        name="poblacion_por_ccaa",
        description="Get population by autonomous community.",
        arguments=[],
    ),
    "poblacion_por_edad": Prompt(
        name="poblacion_por_edad",
        description="Get population pyramid data.",
        arguments=[],
    ),
    "movimiento_natural": Prompt(
        name="movimiento_natural",
        description="Get birth and death statistics.",
        arguments=[],
    ),
    "migraciones": Prompt(
        name="migraciones",
        description="Get migration statistics.",
        arguments=[],
    ),
    "esperanza_vida": Prompt(
        name="esperanza_vida",
        description="Get life expectancy data.",
        arguments=[],
    ),
    # =========================================================================
    # Sectoral Statistics
    # =========================================================================
    "turismo": Prompt(
        name="turismo",
        description="Get tourism statistics (arrivals, spending).",
        arguments=[
            PromptArgument(
                name="tipo",
                description="Type: 'frontur' (arrivals) or 'egatur' (spending)",
                required=False,
            ),
        ],
    ),
    "comercio_exterior": Prompt(
        name="comercio_exterior",
        description="Get import/export statistics.",
        arguments=[],
    ),
    "industria": Prompt(
        name="industria",
        description="Get industrial production index.",
        arguments=[],
    ),
    "construccion": Prompt(
        name="construccion",
        description="Get construction sector statistics.",
        arguments=[],
    ),
    "servicios": Prompt(
        name="servicios",
        description="Get services sector statistics.",
        arguments=[],
    ),
    "comercio_minorista": Prompt(
        name="comercio_minorista",
        description="Get retail trade statistics.",
        arguments=[],
    ),
    # =========================================================================
    # Housing and Real Estate
    # =========================================================================
    "precio_vivienda": Prompt(
        name="precio_vivienda",
        description="Get housing price index.",
        arguments=[],
    ),
    "hipotecas": Prompt(
        name="hipotecas",
        description="Get mortgage statistics.",
        arguments=[],
    ),
    "viviendas_iniciadas": Prompt(
        name="viviendas_iniciadas",
        description="Get new housing starts data.",
        arguments=[],
    ),
    # =========================================================================
    # Other Indicators
    # =========================================================================
    "salarios": Prompt(
        name="salarios",
        description="Get wage and salary statistics.",
        arguments=[],
    ),
    "costes_laborales": Prompt(
        name="costes_laborales",
        description="Get labor cost index.",
        arguments=[],
    ),
    "empresas_activas": Prompt(
        name="empresas_activas",
        description="Get active companies statistics (DIRCE).",
        arguments=[],
    ),
    "condiciones_vida": Prompt(
        name="condiciones_vida",
        description="Get living conditions survey data.",
        arguments=[],
    ),
    # =========================================================================
    # Data Retrieval
    # =========================================================================
    "datos_tabla": Prompt(
        name="datos_tabla",
        description="Get data from a specific INE table.",
        arguments=[
            PromptArgument(
                name="tabla_id",
                description="Table ID from INE",
                required=True,
            ),
            PromptArgument(
                name="periodos",
                description="Number of periods (default: 12)",
                required=False,
            ),
        ],
    ),
    "datos_serie": Prompt(
        name="datos_serie",
        description="Get data from a specific time series.",
        arguments=[
            PromptArgument(
                name="serie_id",
                description="Series code from INE",
                required=True,
            ),
            PromptArgument(
                name="periodos",
                description="Number of periods (default: 12)",
                required=False,
            ),
        ],
    ),
    "comparar_periodos": Prompt(
        name="comparar_periodos",
        description="Compare statistics between two periods.",
        arguments=[
            PromptArgument(
                name="operacion",
                description="Operation code (e.g., 'IPC', 'EPA')",
                required=True,
            ),
            PromptArgument(
                name="periodo1",
                description="First period",
                required=True,
            ),
            PromptArgument(
                name="periodo2",
                description="Second period",
                required=True,
            ),
        ],
    ),
}


def get_ine_prompt_content(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Generate INE prompt content."""
    args = arguments or {}

    # =========================================================================
    # General Discovery
    # =========================================================================
    if name == "operaciones_estadisticas":
        return GetPromptResult(
            description="List INE operations",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista todas las operaciones estadísticas disponibles en el INE.

Pasos:
1. Usa get_ine_operations
2. Agrupa las operaciones por categoría:
   - Indicadores económicos (IPC, PIB, etc.)
   - Empleo (EPA, etc.)
   - Demografía (Censo, Padrón, etc.)
   - Sectoriales (Turismo, Comercio, etc.)
3. Muestra código y nombre de cada operación
4. Indica la frecuencia de actualización (mensual, trimestral, anual)""",
                    ),
                ),
            ],
        )

    elif name == "buscar_estadistica":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Search statistics about {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca operaciones estadísticas sobre: {tema}

Pasos:
1. Usa get_ine_operations para ver todas las operaciones
2. Filtra las relacionadas con "{tema}"
3. Para las más relevantes, usa search_ine_tables para ver tablas disponibles
4. Muestra ejemplos de qué datos se pueden obtener""",
                    ),
                ),
            ],
        )

    elif name == "tablas_operacion":
        operacion = args.get("operacion", "")
        return GetPromptResult(
            description=f"Tables for {operacion}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Lista las tablas disponibles para la operación: {operacion}

Pasos:
1. Usa search_ine_tables con operation_id="{operacion}"
2. Muestra ID y nombre de cada tabla
3. Agrupa por categoría si es posible
4. Indica cuáles son las más utilizadas""",
                    ),
                ),
            ],
        )

    elif name == "variables_operacion":
        operacion = args.get("operacion", "")
        return GetPromptResult(
            description=f"Variables for {operacion}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Lista las variables disponibles para la operación: {operacion}

Pasos:
1. Usa get_ine_variables con operation_id="{operacion}"
2. Muestra ID, código y nombre de cada variable
3. Explica qué representa cada variable""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Key Economic Indicators
    # =========================================================================
    elif name == "ipc_inflacion":
        periodos = args.get("periodos", "12")
        return GetPromptResult(
            description="CPI inflation data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén los datos del IPC (Índice de Precios al Consumo).

Pasos:
1. Usa search_ine_tables con operation_id="IPC"
2. Busca la tabla de variación anual del índice general
3. Usa get_ine_table_data con nult={periodos}
4. Muestra:
   - Tasa de inflación actual (variación anual)
   - Evolución de los últimos {periodos} meses
   - Tendencia (subiendo/bajando)
   - Comparación con el objetivo del BCE (2%)""",
                    ),
                ),
            ],
        )

    elif name == "ipc_por_grupos":
        return GetPromptResult(
            description="CPI by groups",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén el IPC desglosado por grupos de productos.

Pasos:
1. Usa search_ine_tables con operation_id="IPC"
2. Busca tablas de variación por grupos
3. Muestra la inflación por grupos:
   - Alimentos y bebidas no alcohólicas
   - Vivienda
   - Transporte
   - Comunicaciones
   - Ocio y cultura
   - etc.
4. Identifica qué grupos suben/bajan más""",
                    ),
                ),
            ],
        )

    elif name == "inflacion_subyacente":
        return GetPromptResult(
            description="Core inflation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén la inflación subyacente (sin energía ni alimentos frescos).

Pasos:
1. Usa search_ine_tables con operation_id="IPC"
2. Busca la tabla de inflación subyacente
3. Compara con la inflación general
4. Explica la diferencia y qué indica cada una""",
                    ),
                ),
            ],
        )

    elif name == "pib_trimestral":
        periodos = args.get("periodos", "8")
        return GetPromptResult(
            description="Quarterly GDP",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén el crecimiento del PIB trimestral.

Pasos:
1. Usa get_ine_operation con operation_id="CNE" o "PIB"
2. Busca tablas de tasas de variación trimestral
3. Usa get_ine_table_data con nult={periodos}
4. Muestra:
   - Crecimiento trimestral
   - Crecimiento interanual
   - Evolución de los últimos {periodos} trimestres
   - Comparación con la zona euro""",
                    ),
                ),
            ],
        )

    elif name == "pib_por_sectores":
        return GetPromptResult(
            description="GDP by sectors",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén el PIB desglosado por sectores económicos.

Pasos:
1. Busca tablas de contabilidad nacional por ramas
2. Muestra contribución al PIB de:
   - Agricultura
   - Industria
   - Construcción
   - Servicios
3. Muestra variación respecto al año anterior""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Employment Statistics
    # =========================================================================
    elif name == "epa_paro":
        periodos = args.get("periodos", "8")
        return GetPromptResult(
            description="Unemployment rate",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén la tasa de paro de la EPA.

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca la tabla de tasas de paro
3. Usa get_ine_table_data con nult={periodos}
4. Muestra:
   - Tasa de paro actual
   - Número de parados
   - Evolución de los últimos {periodos} trimestres
   - Comparación con la media europea""",
                    ),
                ),
            ],
        )

    elif name == "epa_ocupados":
        return GetPromptResult(
            description="Employment figures",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén los datos de ocupación de la EPA.

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca tablas de ocupados
3. Muestra:
   - Total de ocupados
   - Por sectores (agricultura, industria, construcción, servicios)
   - Tasa de empleo
   - Variación trimestral y anual""",
                    ),
                ),
            ],
        )

    elif name == "epa_por_sexo":
        return GetPromptResult(
            description="Employment by sex",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de empleo desglosados por sexo.

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca tablas con desglose por sexo
3. Muestra:
   - Tasa de paro hombres vs mujeres
   - Tasa de actividad por sexo
   - Brecha de género en empleo""",
                    ),
                ),
            ],
        )

    elif name == "epa_por_edad":
        return GetPromptResult(
            description="Employment by age",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de empleo desglosados por grupos de edad.

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca tablas con desglose por edad
3. Muestra:
   - Tasa de paro por grupos de edad
   - Paro juvenil (16-24 años)
   - Empleo de mayores de 55 años""",
                    ),
                ),
            ],
        )

    elif name == "epa_por_comunidad":
        return GetPromptResult(
            description="Employment by region",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de empleo por comunidad autónoma.

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca tablas con desglose por CCAA
3. Muestra:
   - Tasa de paro por CCAA
   - CCAA con más/menos paro
   - Evolución regional""",
                    ),
                ),
            ],
        )

    elif name == "paro_juvenil":
        return GetPromptResult(
            description="Youth unemployment",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén la tasa de paro juvenil (menores de 25 años).

Pasos:
1. Usa search_ine_tables con operation_id="EPA"
2. Busca tablas de paro por edad
3. Filtra el grupo 16-24 años
4. Muestra:
   - Tasa de paro juvenil actual
   - Comparación con la tasa general
   - Evolución reciente
   - Comparación con la UE""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Demographics
    # =========================================================================
    elif name == "poblacion_espana":
        return GetPromptResult(
            description="Spain population",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén los datos de población total de España.

Pasos:
1. Busca operaciones de población (Padrón, Censo)
2. Muestra:
   - Población total actual
   - Evolución en los últimos años
   - Densidad de población
   - Comparación con otros países UE""",
                    ),
                ),
            ],
        )

    elif name == "poblacion_por_ccaa":
        return GetPromptResult(
            description="Population by region",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén la población por comunidad autónoma.

Pasos:
1. Busca tablas de población por CCAA
2. Muestra:
   - Población de cada CCAA
   - Porcentaje sobre el total
   - CCAA más y menos pobladas
   - Tendencias (crecen/decrecen)""",
                    ),
                ),
            ],
        )

    elif name == "poblacion_por_edad":
        return GetPromptResult(
            description="Population pyramid",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén la pirámide de población de España.

Pasos:
1. Busca tablas de población por grupos de edad
2. Muestra:
   - Distribución por grupos quinquenales
   - Ratio de dependencia
   - Índice de envejecimiento
   - Comparación temporal""",
                    ),
                ),
            ],
        )

    elif name == "movimiento_natural":
        return GetPromptResult(
            description="Natural movement",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de nacimientos y defunciones.

Pasos:
1. Busca la operación de movimiento natural de población
2. Muestra:
   - Número de nacimientos
   - Número de defunciones
   - Crecimiento vegetativo
   - Tasa de natalidad y mortalidad""",
                    ),
                ),
            ],
        )

    elif name == "migraciones":
        return GetPromptResult(
            description="Migration statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de migraciones.

Pasos:
1. Busca operaciones de estadística de migraciones
2. Muestra:
   - Inmigración (llegadas)
   - Emigración (salidas)
   - Saldo migratorio
   - Principales países de origen/destino""",
                    ),
                ),
            ],
        )

    elif name == "esperanza_vida":
        return GetPromptResult(
            description="Life expectancy",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de esperanza de vida.

Pasos:
1. Busca tablas de mortalidad y esperanza de vida
2. Muestra:
   - Esperanza de vida al nacer
   - Diferencia hombres/mujeres
   - Evolución histórica
   - Comparación con la UE""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Sectoral Statistics
    # =========================================================================
    elif name == "turismo":
        tipo = args.get("tipo")
        tipo_text = f" ({tipo})" if tipo else ""
        return GetPromptResult(
            description="Tourism statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén estadísticas de turismo{tipo_text}.

Pasos:
1. Busca operaciones: FRONTUR (llegadas) y EGATUR (gasto)
2. Muestra:
   - Número de turistas extranjeros
   - Gasto turístico total
   - Principales países emisores
   - Destinos más visitados
   - Estacionalidad""",
                    ),
                ),
            ],
        )

    elif name == "comercio_exterior":
        return GetPromptResult(
            description="Foreign trade",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de comercio exterior.

Pasos:
1. Busca estadísticas de importaciones y exportaciones
2. Muestra:
   - Exportaciones totales
   - Importaciones totales
   - Balanza comercial
   - Principales socios comerciales
   - Productos más exportados/importados""",
                    ),
                ),
            ],
        )

    elif name == "industria":
        return GetPromptResult(
            description="Industrial production",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén el Índice de Producción Industrial (IPI).

Pasos:
1. Busca la operación IPI
2. Muestra:
   - Índice general
   - Variación mensual y anual
   - Desglose por ramas industriales
   - Tendencia""",
                    ),
                ),
            ],
        )

    elif name == "construccion":
        return GetPromptResult(
            description="Construction statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas del sector de la construcción.

Pasos:
1. Busca indicadores de construcción
2. Muestra:
   - Visados de obra nueva
   - Licitación oficial
   - Empleo en construcción
   - Costes de construcción""",
                    ),
                ),
            ],
        )

    elif name == "servicios":
        return GetPromptResult(
            description="Services statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén indicadores del sector servicios.

Pasos:
1. Busca el Indicador de Actividad del Sector Servicios
2. Muestra:
   - Índice de cifra de negocios
   - Variación mensual y anual
   - Desglose por subsectores""",
                    ),
                ),
            ],
        )

    elif name == "comercio_minorista":
        return GetPromptResult(
            description="Retail trade",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de comercio minorista.

Pasos:
1. Busca Índices de Comercio Minorista
2. Muestra:
   - Índice de ventas
   - Variación mensual y anual
   - Grandes superficies vs pequeño comercio
   - Tendencias de consumo""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Housing and Real Estate
    # =========================================================================
    elif name == "precio_vivienda":
        return GetPromptResult(
            description="Housing prices",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén el índice de precios de la vivienda.

Pasos:
1. Busca el Índice de Precios de Vivienda (IPV)
2. Muestra:
   - Variación trimestral
   - Variación anual
   - Vivienda nueva vs segunda mano
   - Precios por CCAA""",
                    ),
                ),
            ],
        )

    elif name == "hipotecas":
        return GetPromptResult(
            description="Mortgage statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de hipotecas.

Pasos:
1. Busca la estadística de hipotecas
2. Muestra:
   - Número de hipotecas constituidas
   - Importe medio
   - Tipo de interés medio
   - Evolución mensual/anual""",
                    ),
                ),
            ],
        )

    elif name == "viviendas_iniciadas":
        return GetPromptResult(
            description="Housing starts",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de viviendas iniciadas.

Pasos:
1. Busca estadísticas de visados y licencias
2. Muestra:
   - Viviendas visadas
   - Comparación con periodos anteriores
   - Distribución por CCAA""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Other Indicators
    # =========================================================================
    elif name == "salarios":
        return GetPromptResult(
            description="Wage statistics",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de salarios.

Pasos:
1. Busca la Encuesta Anual de Estructura Salarial
2. Muestra:
   - Salario medio
   - Salario mediano
   - Diferencia por sectores
   - Brecha salarial de género""",
                    ),
                ),
            ],
        )

    elif name == "costes_laborales":
        return GetPromptResult(
            description="Labor costs",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén el Índice de Costes Laborales.

Pasos:
1. Busca la operación de Costes Laborales
2. Muestra:
   - Coste laboral por trabajador
   - Variación trimestral y anual
   - Desglose: coste salarial + otros costes""",
                    ),
                ),
            ],
        )

    elif name == "empresas_activas":
        return GetPromptResult(
            description="Active companies",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén estadísticas de empresas activas (DIRCE).

Pasos:
1. Busca el Directorio Central de Empresas
2. Muestra:
   - Total de empresas activas
   - Distribución por tamaño (micropymes, pymes, grandes)
   - Distribución por sector
   - Altas y bajas de empresas""",
                    ),
                ),
            ],
        )

    elif name == "condiciones_vida":
        return GetPromptResult(
            description="Living conditions",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Obtén datos de la Encuesta de Condiciones de Vida.

Pasos:
1. Busca la operación ECV
2. Muestra:
   - Renta media por hogar
   - Tasa de riesgo de pobreza
   - Carencia material
   - Satisfacción con la vida""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Data Retrieval
    # =========================================================================
    elif name == "datos_tabla":
        tabla_id = args.get("tabla_id", "")
        periodos = args.get("periodos", "12")
        return GetPromptResult(
            description=f"Table data {tabla_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén los datos de la tabla INE: {tabla_id}

Pasos:
1. Usa get_ine_table_data con table_id="{tabla_id}" y nult={periodos}
2. Muestra los datos en formato tabular
3. Calcula variaciones si es posible""",
                    ),
                ),
            ],
        )

    elif name == "datos_serie":
        serie_id = args.get("serie_id", "")
        periodos = args.get("periodos", "12")
        return GetPromptResult(
            description=f"Series data {serie_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén los datos de la serie INE: {serie_id}

Pasos:
1. Usa get_ine_series_data con series_code="{serie_id}" y nult={periodos}
2. Muestra la evolución temporal
3. Calcula tendencia y variaciones""",
                    ),
                ),
            ],
        )

    elif name == "comparar_periodos":
        operacion = args.get("operacion", "")
        periodo1 = args.get("periodo1", "")
        periodo2 = args.get("periodo2", "")
        return GetPromptResult(
            description=f"Compare periods for {operacion}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Compara los datos de {operacion} entre {periodo1} y {periodo2}.

Pasos:
1. Usa search_ine_tables para encontrar las tablas de {operacion}
2. Obtén los datos para ambos periodos
3. Calcula las diferencias
4. Muestra una comparativa visual""",
                    ),
                ),
            ],
        )

    else:
        raise ValueError(f"Unknown INE prompt: {name}")
