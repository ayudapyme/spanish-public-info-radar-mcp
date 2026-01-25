"""Combined prompts for cross-source research.

Prompts that combine multiple data sources for comprehensive analysis.
"""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

COMBINED_PROMPTS: dict[str, Prompt] = {
    # =========================================================================
    # Economic Overview
    # =========================================================================
    "panorama_economico": Prompt(
        name="panorama_economico",
        description="Comprehensive Spanish economic overview (INE + BOE).",
        arguments=[],
    ),
    "indicadores_clave": Prompt(
        name="indicadores_clave",
        description="Key economic indicators dashboard.",
        arguments=[],
    ),
    "coyuntura_economica": Prompt(
        name="coyuntura_economica",
        description="Current economic situation analysis.",
        arguments=[],
    ),
    # =========================================================================
    # Company Research
    # =========================================================================
    "investigar_empresa": Prompt(
        name="investigar_empresa",
        description="Comprehensive company investigation (BDNS + BORME).",
        arguments=[
            PromptArgument(
                name="nif",
                description="Company NIF/CIF",
                required=True,
            ),
            PromptArgument(
                name="nombre",
                description="Company name (for BORME search)",
                required=False,
            ),
        ],
    ),
    "due_diligence": Prompt(
        name="due_diligence",
        description="Due diligence report on an entity.",
        arguments=[
            PromptArgument(
                name="nif",
                description="Entity NIF/CIF",
                required=True,
            ),
        ],
    ),
    "competidores_sector": Prompt(
        name="competidores_sector",
        description="Analyze competitors in a sector via grants and registry.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Sector Analysis
    # =========================================================================
    "analisis_sector": Prompt(
        name="analisis_sector",
        description="Complete sector analysis (grants + legislation + statistics).",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze (e.g., 'energia', 'turismo', 'tecnologia')",
                required=True,
            ),
        ],
    ),
    "oportunidades_sector": Prompt(
        name="oportunidades_sector",
        description="Find opportunities in a sector (grants + open data).",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze",
                required=True,
            ),
        ],
    ),
    "marco_regulatorio": Prompt(
        name="marco_regulatorio",
        description="Regulatory framework for a sector (BOE + recent changes).",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Funding and Grants
    # =========================================================================
    "financiacion_disponible": Prompt(
        name="financiacion_disponible",
        description="All available public funding (current open grants).",
        arguments=[
            PromptArgument(
                name="perfil",
                description="Profile: 'pyme', 'autonomo', 'startup', 'gran_empresa'",
                required=False,
            ),
        ],
    ),
    "subvenciones_y_normativa": Prompt(
        name="subvenciones_y_normativa",
        description="Grants and their regulatory framework.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze",
                required=True,
            ),
        ],
    ),
    "historial_subvenciones_sector": Prompt(
        name="historial_subvenciones_sector",
        description="Grant history analysis for a sector.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to analyze",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Geographic Analysis
    # =========================================================================
    "analisis_territorial": Prompt(
        name="analisis_territorial",
        description="Territorial analysis of a region (statistics + open data).",
        arguments=[
            PromptArgument(
                name="territorio",
                description="Territory: CCAA or province name",
                required=True,
            ),
        ],
    ),
    "comparar_territorios": Prompt(
        name="comparar_territorios",
        description="Compare two territories on key indicators.",
        arguments=[
            PromptArgument(
                name="territorio1",
                description="First territory",
                required=True,
            ),
            PromptArgument(
                name="territorio2",
                description="Second territory",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Monitoring
    # =========================================================================
    "monitor_diario": Prompt(
        name="monitor_diario",
        description="Daily monitoring: BOE + BORME + recent grants.",
        arguments=[],
    ),
    "monitor_sector": Prompt(
        name="monitor_sector",
        description="Sector monitoring: legislation + grants + statistics.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector to monitor",
                required=True,
            ),
        ],
    ),
    "alertas_legislativas": Prompt(
        name="alertas_legislativas",
        description="Recent legislative changes affecting a topic.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to monitor",
                required=True,
            ),
            PromptArgument(
                name="dias",
                description="Days to look back (default: 7)",
                required=False,
            ),
        ],
    ),
    # =========================================================================
    # Research
    # =========================================================================
    "investigar_tema": Prompt(
        name="investigar_tema",
        description="Comprehensive topic research across all sources.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to research",
                required=True,
            ),
        ],
    ),
    "datos_para_estudio": Prompt(
        name="datos_para_estudio",
        description="Find all available data for a research study.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Research topic",
                required=True,
            ),
        ],
    ),
    "fuentes_oficiales": Prompt(
        name="fuentes_oficiales",
        description="List all official data sources on a topic.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Topic to search",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Specific Use Cases
    # =========================================================================
    "crear_empresa": Prompt(
        name="crear_empresa",
        description="Information for starting a business (grants + legislation).",
        arguments=[
            PromptArgument(
                name="tipo",
                description="Business type or sector",
                required=True,
            ),
        ],
    ),
    "exportar": Prompt(
        name="exportar",
        description="Information for exporting (grants + statistics + regulations).",
        arguments=[
            PromptArgument(
                name="sector",
                description="Export sector",
                required=False,
            ),
        ],
    ),
    "contratar_empleados": Prompt(
        name="contratar_empleados",
        description="Employment information (grants + labor legislation).",
        arguments=[],
    ),
    "sostenibilidad_empresa": Prompt(
        name="sostenibilidad_empresa",
        description="Sustainability for businesses (grants + regulations + data).",
        arguments=[],
    ),
}


def get_combined_prompt_content(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Generate combined prompt content."""
    args = arguments or {}

    # =========================================================================
    # Economic Overview
    # =========================================================================
    if name == "panorama_economico":
        return GetPromptResult(
            description="Economic overview",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Dame un panorama económico completo de España.

Pasos:
1. INFLACIÓN (INE):
   - Usa search_ine_tables con operation_id="IPC"
   - Obtén la tasa de inflación actual

2. EMPLEO (INE):
   - Usa search_ine_tables con operation_id="EPA"
   - Obtén la tasa de paro actual

3. PIB (INE):
   - Busca datos de crecimiento económico

4. NOVEDADES (BOE):
   - Usa get_boe_summary para ver publicaciones recientes
   - Filtra las de contenido económico

5. SUBVENCIONES (BDNS):
   - Usa search_grants para ver convocatorias abiertas

Proporciona un resumen ejecutivo con:
- Indicadores principales
- Tendencias
- Novedades legislativas relevantes
- Oportunidades de financiación""",
                    ),
                ),
            ],
        )

    elif name == "indicadores_clave":
        return GetPromptResult(
            description="Key indicators",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Muestra un dashboard de indicadores económicos clave.

Indicadores a obtener (INE):
1. IPC - Inflación
2. EPA - Tasa de paro
3. PIB - Crecimiento
4. Comercio exterior
5. Turismo

Para cada uno:
- Valor actual
- Variación mensual/trimestral
- Variación anual
- Tendencia""",
                    ),
                ),
            ],
        )

    elif name == "coyuntura_economica":
        return GetPromptResult(
            description="Economic situation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Analiza la coyuntura económica actual.

Pasos:
1. Obtén los últimos datos del INE
2. Revisa el BOE reciente para medidas económicas
3. Busca subvenciones activas (indicador de política económica)
4. Contextualiza con la situación europea

Proporciona un análisis de:
- Situación actual
- Tendencias
- Riesgos y oportunidades
- Perspectivas""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Company Research
    # =========================================================================
    elif name == "investigar_empresa":
        nif = args.get("nif", "")
        nombre = args.get("nombre")
        nombre_text = f" ({nombre})" if nombre else ""
        return GetPromptResult(
            description=f"Investigate company {nif}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Investiga la empresa con NIF: {nif}{nombre_text}

1. SUBVENCIONES RECIBIDAS (BDNS):
   - Usa search_grant_awards con beneficiary_nif="{nif}"
   - Lista todas las subvenciones recibidas
   - Calcula el total recibido

2. REGISTRO MERCANTIL (BORME):
   - Usa get_borme_summary reciente
   - Busca actos relacionados con esta empresa
   - Nombramientos, cambios de capital, etc.

3. RESUMEN:
   - Historial de subvenciones
   - Movimientos mercantiles recientes
   - Perfil de la empresa""",
                    ),
                ),
            ],
        )

    elif name == "due_diligence":
        nif = args.get("nif", "")
        return GetPromptResult(
            description=f"Due diligence {nif}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Realiza un informe de due diligence para la entidad: {nif}

1. HISTORIAL DE SUBVENCIONES:
   - search_grant_awards con beneficiary_nif="{nif}"
   - Analiza patrones de financiación

2. MOVIMIENTOS MERCANTILES:
   - Busca en BORME histórico
   - Cambios de administradores
   - Modificaciones estatutarias

3. CONTEXTO SECTORIAL:
   - Identifica el sector
   - Normativa aplicable
   - Competidores que reciben subvenciones

4. INFORME:
   - Resumen de hallazgos
   - Señales de alerta si las hay
   - Recomendaciones""",
                    ),
                ),
            ],
        )

    elif name == "competidores_sector":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Competitors in {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza competidores en el sector: {sector}

Pasos:
1. SUBVENCIONES DEL SECTOR:
   - Usa search_grants buscando "{sector}"
   - Identifica convocatorias del sector

2. BENEFICIARIOS:
   - Usa search_grant_awards para ver quién recibe
   - Agrupa por beneficiario

3. CONSTITUCIONES:
   - Busca en BORME empresas del sector
   - Nuevas empresas = nuevos competidores

4. ANÁLISIS:
   - Top beneficiarios de subvenciones
   - Nuevos entrantes
   - Tendencias del sector""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Sector Analysis
    # =========================================================================
    elif name == "analisis_sector":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Sector analysis: {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Análisis completo del sector: {sector}

1. ESTADÍSTICAS (INE):
   - Busca operaciones relacionadas con "{sector}"
   - Obtén indicadores del sector

2. LEGISLACIÓN (BOE):
   - Usa search_legislation buscando "{sector}"
   - Identifica normativa aplicable

3. SUBVENCIONES (BDNS):
   - Busca convocatorias del sector
   - Analiza tendencias de financiación

4. DATOS ABIERTOS:
   - Usa search_open_data con "{sector}"
   - Identifica fuentes de datos

5. INFORME:
   - Tamaño y evolución del sector
   - Marco regulatorio
   - Oportunidades de financiación
   - Fuentes de datos disponibles""",
                    ),
                ),
            ],
        )

    elif name == "oportunidades_sector":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Opportunities in {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca oportunidades en el sector: {sector}

1. SUBVENCIONES ABIERTAS:
   - search_grants con "{sector}"
   - Filtra las activas

2. PRÓXIMAS CONVOCATORIAS:
   - Revisa patrones de años anteriores
   - Anticipa convocatorias

3. DATOS PARA OPORTUNIDADES:
   - search_open_data del sector
   - Identifica nichos de mercado

4. RESUMEN:
   - Financiación disponible ahora
   - Financiación esperada
   - Áreas de oportunidad""",
                    ),
                ),
            ],
        )

    elif name == "marco_regulatorio":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Regulatory framework: {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza el marco regulatorio del sector: {sector}

1. LEGISLACIÓN VIGENTE:
   - search_legislation con "{sector}"
   - Solo normativa vigente

2. CAMBIOS RECIENTES:
   - search_recent_boe últimos 30 días
   - Filtra por "{sector}"

3. NORMATIVA RELACIONADA:
   - Para las leyes principales, usa find_related_laws

4. RESUMEN:
   - Normas principales
   - Cambios recientes
   - Próximos cambios anunciados""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Funding and Grants
    # =========================================================================
    elif name == "financiacion_disponible":
        perfil = args.get("perfil")
        perfil_text = f" para {perfil}" if perfil else ""
        return GetPromptResult(
            description="Available funding",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca toda la financiación pública disponible{perfil_text}.

1. CONVOCATORIAS ABIERTAS:
   - search_grants con fechas recientes
   - Filtra las que siguen abiertas

2. POR TIPO:
   - Subvenciones a fondo perdido
   - Préstamos bonificados
   - Avales

3. POR SECTOR:
   - Agrupa por temática

4. RESUMEN:
   - Total disponible
   - Plazos de solicitud
   - Requisitos principales""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_y_normativa":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Grants and regulations: {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza subvenciones y su marco normativo en: {sector}

1. SUBVENCIONES:
   - search_grants con "{sector}"
   - Lista convocatorias

2. BASES REGULADORAS:
   - Para las principales, identifica la normativa
   - search_legislation relacionada

3. REQUISITOS LEGALES:
   - Normativa de subvenciones general
   - Requisitos sectoriales

4. RESUMEN:
   - Subvenciones disponibles
   - Marco legal aplicable
   - Obligaciones del beneficiario""",
                    ),
                ),
            ],
        )

    elif name == "historial_subvenciones_sector":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Grant history: {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza el historial de subvenciones en: {sector}

1. CONVOCATORIAS HISTÓRICAS:
   - search_grants del sector
   - Agrupa por año

2. CONCESIONES:
   - search_grant_awards
   - Principales beneficiarios

3. TENDENCIAS:
   - Evolución del presupuesto
   - Cambios en prioridades

4. PREDICCIONES:
   - Basado en histórico, ¿qué esperar?""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Geographic Analysis
    # =========================================================================
    elif name == "analisis_territorial":
        territorio = args.get("territorio", "")
        return GetPromptResult(
            description=f"Territorial analysis: {territorio}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Análisis territorial de: {territorio}

1. ESTADÍSTICAS (INE):
   - Población
   - Empleo
   - PIB per cápita
   - Indicadores específicos

2. DATOS ABIERTOS:
   - search_open_data del territorio
   - Portales de datos locales

3. EMPRESAS (BORME):
   - Actividad mercantil reciente
   - Nuevas empresas

4. SUBVENCIONES:
   - Convocatorias específicas
   - Beneficiarios del territorio

5. INFORME:
   - Perfil socioeconómico
   - Fortalezas y debilidades
   - Fuentes de datos disponibles""",
                    ),
                ),
            ],
        )

    elif name == "comparar_territorios":
        t1 = args.get("territorio1", "")
        t2 = args.get("territorio2", "")
        return GetPromptResult(
            description=f"Compare {t1} vs {t2}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Compara {t1} con {t2}.

Para cada territorio obtén:
1. Población (INE)
2. Tasa de paro (EPA)
3. PIB per cápita
4. Empresas activas
5. Subvenciones recibidas

Presenta una comparativa con:
- Tabla de indicadores
- Fortalezas de cada uno
- Conclusiones""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Monitoring
    # =========================================================================
    elif name == "monitor_diario":
        return GetPromptResult(
            description="Daily monitoring",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Monitor diario de novedades.

1. BOE:
   - get_boe_summary de hoy
   - Destacar lo más relevante

2. BORME:
   - get_borme_summary de hoy
   - Movimientos destacados

3. SUBVENCIONES:
   - search_grants últimos 3 días
   - Nuevas convocatorias

4. RESUMEN EJECUTIVO:
   - Principales novedades
   - Alertas importantes""",
                    ),
                ),
            ],
        )

    elif name == "monitor_sector":
        sector = args.get("sector", "")
        return GetPromptResult(
            description=f"Monitor: {sector}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Monitoriza el sector: {sector}

1. BOE RECIENTE:
   - search_recent_boe con "{sector}"
   - Novedades legislativas

2. SUBVENCIONES:
   - search_grants del sector
   - Nuevas convocatorias

3. ESTADÍSTICAS:
   - Indicadores del sector actualizados

4. INFORME:
   - Novedades de la semana
   - Cambios relevantes
   - Oportunidades detectadas""",
                    ),
                ),
            ],
        )

    elif name == "alertas_legislativas":
        tema = args.get("tema", "")
        dias = args.get("dias", "7")
        return GetPromptResult(
            description=f"Legislative alerts: {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Alertas legislativas sobre: {tema} (últimos {dias} días)

Pasos:
1. search_recent_boe con days_back={dias} y search_terms="{tema}"
2. Filtra sección 1 (disposiciones generales)
3. Para cada novedad relevante:
   - Título y tipo de norma
   - Resumen del contenido
   - Impacto potencial
4. Ordena por importancia""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Research
    # =========================================================================
    elif name == "investigar_tema":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Research: {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Investigación completa sobre: {tema}

1. ESTADÍSTICAS:
   - Busca operaciones INE relacionadas
   - Obtén datos cuantitativos

2. LEGISLACIÓN:
   - search_legislation con "{tema}"
   - Marco normativo aplicable

3. SUBVENCIONES:
   - search_grants con "{tema}"
   - Financiación pública disponible

4. DATOS ABIERTOS:
   - search_open_data con "{tema}"
   - Fuentes de datos

5. INFORME:
   - Estado de la cuestión
   - Datos disponibles
   - Normativa aplicable
   - Financiación disponible""",
                    ),
                ),
            ],
        )

    elif name == "datos_para_estudio":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Data for study: {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Encuentra datos para un estudio sobre: {tema}

1. INE:
   - Operaciones estadísticas relevantes
   - Tablas disponibles

2. DATOS.GOB.ES:
   - Datasets relacionados
   - Formatos disponibles (CSV, JSON)

3. BOE:
   - Informes y estudios oficiales
   - Memorias de leyes

4. INVENTARIO:
   - Lista todas las fuentes
   - Indica formato y acceso
   - Evalúa calidad de datos""",
                    ),
                ),
            ],
        )

    elif name == "fuentes_oficiales":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Official sources: {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Lista fuentes oficiales sobre: {tema}

Busca en:
1. INE - Estadísticas
2. BOE - Legislación y documentos
3. datos.gob.es - Datasets
4. BDNS - Subvenciones

Para cada fuente indica:
- Tipo de información
- Frecuencia de actualización
- Cómo acceder
- Calidad/fiabilidad""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Specific Use Cases
    # =========================================================================
    elif name == "crear_empresa":
        tipo = args.get("tipo", "")
        return GetPromptResult(
            description=f"Start business: {tipo}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Información para crear una empresa de: {tipo}

1. NORMATIVA:
   - search_legislation con "sociedad empresa"
   - Requisitos legales

2. SUBVENCIONES PARA EMPRENDEDORES:
   - search_grants con "emprendedor startup"
   - Ayudas al inicio de actividad

3. REGISTROS:
   - Info sobre inscripción en BORME

4. GUÍA:
   - Pasos para constituir
   - Subvenciones disponibles
   - Normativa aplicable""",
                    ),
                ),
            ],
        )

    elif name == "exportar":
        sector = args.get("sector")
        sector_text = f" en el sector {sector}" if sector else ""
        return GetPromptResult(
            description="Export information",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Información para exportar{sector_text}.

1. ESTADÍSTICAS (INE):
   - Datos de comercio exterior
   - Principales destinos

2. SUBVENCIONES:
   - search_grants con "exportación internacionalización"
   - Ayudas ICEX

3. NORMATIVA:
   - Regulación aduanera
   - Requisitos por mercado

4. GUÍA:
   - Mercados objetivo
   - Financiación disponible
   - Requisitos legales""",
                    ),
                ),
            ],
        )

    elif name == "contratar_empleados":
        return GetPromptResult(
            description="Employment information",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Información para contratar empleados.

1. NORMATIVA LABORAL:
   - search_legislation con "estatuto trabajadores"
   - Tipos de contratos

2. SUBVENCIONES AL EMPLEO:
   - search_grants con "empleo contratación"
   - Bonificaciones disponibles

3. ESTADÍSTICAS:
   - Salarios medios por sector
   - Costes laborales

4. RESUMEN:
   - Tipos de contratos
   - Bonificaciones vigentes
   - Costes estimados""",
                    ),
                ),
            ],
        )

    elif name == "sostenibilidad_empresa":
        return GetPromptResult(
            description="Business sustainability",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Información sobre sostenibilidad empresarial.

1. NORMATIVA:
   - search_legislation con "sostenibilidad ESG"
   - Obligaciones de reporting

2. SUBVENCIONES:
   - search_grants con "sostenibilidad verde"
   - Ayudas para transición ecológica

3. DATOS:
   - search_open_data con "emisiones sostenibilidad"
   - Benchmarks y referencias

4. GUÍA:
   - Obligaciones legales
   - Ayudas disponibles
   - Buenas prácticas""",
                    ),
                ),
            ],
        )

    else:
        raise ValueError(f"Unknown combined prompt: {name}")
