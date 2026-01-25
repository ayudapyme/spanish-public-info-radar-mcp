"""datos.gob.es prompts for open data queries.

Prompts for the Spanish National Open Data Catalog.
"""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

DATOS_GOB_PROMPTS: dict[str, Prompt] = {
    # =========================================================================
    # Discovery and Exploration
    # =========================================================================
    "explorar_catalogo": Prompt(
        name="explorar_catalogo",
        description="Explore the open data catalog structure and categories.",
        arguments=[],
    ),
    "categorias_disponibles": Prompt(
        name="categorias_disponibles",
        description="List all available themes/categories in the catalog.",
        arguments=[],
    ),
    "publicadores_catalogo": Prompt(
        name="publicadores_catalogo",
        description="List organizations publishing data in the catalog.",
        arguments=[],
    ),
    "datasets_recientes": Prompt(
        name="datasets_recientes",
        description="Find recently updated datasets.",
        arguments=[
            PromptArgument(
                name="dias",
                description="Number of days to look back (default: 30)",
                required=False,
            ),
        ],
    ),
    # =========================================================================
    # Search by Topic
    # =========================================================================
    "buscar_datasets": Prompt(
        name="buscar_datasets",
        description="Search datasets by keywords.",
        arguments=[
            PromptArgument(
                name="busqueda",
                description="Search terms",
                required=True,
            ),
        ],
    ),
    "datasets_por_tema": Prompt(
        name="datasets_por_tema",
        description="Find datasets in a specific category/theme.",
        arguments=[
            PromptArgument(
                name="tema",
                description="Theme code (e.g., 'medio-ambiente', 'economia', 'salud')",
                required=True,
            ),
        ],
    ),
    "datasets_por_publicador": Prompt(
        name="datasets_por_publicador",
        description="Find datasets from a specific publisher.",
        arguments=[
            PromptArgument(
                name="publicador",
                description="Publisher name or code",
                required=True,
            ),
        ],
    ),
    "datasets_por_formato": Prompt(
        name="datasets_por_formato",
        description="Find datasets available in a specific format.",
        arguments=[
            PromptArgument(
                name="formato",
                description="Format: CSV, JSON, XML, RDF, etc.",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Analysis
    # =========================================================================
    "analizar_dataset": Prompt(
        name="analizar_dataset",
        description="Get detailed analysis of a specific dataset.",
        arguments=[
            PromptArgument(
                name="dataset_id",
                description="Dataset identifier",
                required=True,
            ),
        ],
    ),
    "formatos_dataset": Prompt(
        name="formatos_dataset",
        description="List available download formats for a dataset.",
        arguments=[
            PromptArgument(
                name="dataset_id",
                description="Dataset identifier",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Thematic Searches
    # =========================================================================
    "datos_medio_ambiente": Prompt(
        name="datos_medio_ambiente",
        description="Find environmental datasets (air quality, water, emissions).",
        arguments=[
            PromptArgument(
                name="subtema",
                description="Subtopic: 'aire', 'agua', 'residuos', 'ruido'",
                required=False,
            ),
        ],
    ),
    "datos_transporte": Prompt(
        name="datos_transporte",
        description="Find transport and mobility datasets.",
        arguments=[
            PromptArgument(
                name="tipo",
                description="Type: 'trafico', 'transporte_publico', 'bicicletas'",
                required=False,
            ),
        ],
    ),
    "datos_turismo": Prompt(
        name="datos_turismo",
        description="Find tourism datasets.",
        arguments=[],
    ),
    "datos_economia": Prompt(
        name="datos_economia",
        description="Find economic and business datasets.",
        arguments=[],
    ),
    "datos_salud": Prompt(
        name="datos_salud",
        description="Find health-related datasets.",
        arguments=[],
    ),
    "datos_educacion": Prompt(
        name="datos_educacion",
        description="Find education datasets.",
        arguments=[],
    ),
    "datos_cultura": Prompt(
        name="datos_cultura",
        description="Find culture and heritage datasets.",
        arguments=[],
    ),
    "datos_urbanismo": Prompt(
        name="datos_urbanismo",
        description="Find urban planning and geographic datasets.",
        arguments=[],
    ),
    "datos_energia": Prompt(
        name="datos_energia",
        description="Find energy and utilities datasets.",
        arguments=[],
    ),
    "datos_agricultura": Prompt(
        name="datos_agricultura",
        description="Find agriculture and rural datasets.",
        arguments=[],
    ),
    # =========================================================================
    # Geographic Searches
    # =========================================================================
    "datos_municipio": Prompt(
        name="datos_municipio",
        description="Find datasets from a specific municipality.",
        arguments=[
            PromptArgument(
                name="municipio",
                description="Municipality name (e.g., 'Madrid', 'Barcelona')",
                required=True,
            ),
        ],
    ),
    "datos_comunidad": Prompt(
        name="datos_comunidad",
        description="Find datasets from a specific autonomous community.",
        arguments=[
            PromptArgument(
                name="comunidad",
                description="Community name (e.g., 'Andalucía', 'Cataluña')",
                required=True,
            ),
        ],
    ),
    "datos_nacionales": Prompt(
        name="datos_nacionales",
        description="Find national-level datasets from central government.",
        arguments=[],
    ),
    # =========================================================================
    # API and Technical
    # =========================================================================
    "datasets_con_api": Prompt(
        name="datasets_con_api",
        description="Find datasets that provide API access.",
        arguments=[],
    ),
    "datasets_tiempo_real": Prompt(
        name="datasets_tiempo_real",
        description="Find datasets with real-time or frequent updates.",
        arguments=[],
    ),
    "datos_geoespaciales": Prompt(
        name="datos_geoespaciales",
        description="Find geospatial/GIS datasets.",
        arguments=[],
    ),
}


def get_datos_gob_prompt_content(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Generate datos.gob.es prompt content."""
    args = arguments or {}

    # =========================================================================
    # Discovery and Exploration
    # =========================================================================
    if name == "explorar_catalogo":
        return GetPromptResult(
            description="Explore open data catalog",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Explora el catálogo de datos abiertos de España (datos.gob.es).

Pasos:
1. Usa list_open_data_themes para ver las categorías disponibles
2. Usa list_open_data_publishers para ver los publicadores principales
3. Proporciona un resumen del catálogo:
   - Número aproximado de datasets
   - Principales categorías
   - Principales publicadores
   - Tipos de datos más comunes""",
                    ),
                ),
            ],
        )

    elif name == "categorias_disponibles":
        return GetPromptResult(
            description="List categories",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista todas las categorías/temas disponibles en datos.gob.es.

Pasos:
1. Usa list_open_data_themes
2. Muestra cada categoría con su código
3. Explica brevemente qué tipo de datos contiene cada una
4. Indica cuáles tienen más datasets""",
                    ),
                ),
            ],
        )

    elif name == "publicadores_catalogo":
        return GetPromptResult(
            description="List publishers",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Lista las organizaciones que publican datos en datos.gob.es.

Pasos:
1. Usa list_open_data_publishers
2. Agrupa por tipo:
   - Administración General del Estado
   - Comunidades Autónomas
   - Ayuntamientos
   - Otros organismos
3. Indica los más activos""",
                    ),
                ),
            ],
        )

    elif name == "datasets_recientes":
        dias = args.get("dias", "30")
        return GetPromptResult(
            description="Recent datasets",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets actualizados en los últimos {dias} días.

Pasos:
1. Usa search_open_data para buscar datasets
2. Filtra por fecha de modificación reciente
3. Muestra:
   - Título
   - Publicador
   - Categoría
   - Fecha de actualización
   - Formatos disponibles""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Search by Topic
    # =========================================================================
    elif name == "buscar_datasets":
        busqueda = args.get("busqueda", "")
        return GetPromptResult(
            description=f"Search: {busqueda}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets sobre: {busqueda}

Pasos:
1. Usa search_open_data con query="{busqueda}"
2. Para cada resultado muestra:
   - Título y descripción breve
   - Publicador
   - Categorías
   - Formatos disponibles (CSV, JSON, etc.)
   - Fecha de última actualización
3. Destaca los más relevantes o completos""",
                    ),
                ),
            ],
        )

    elif name == "datasets_por_tema":
        tema = args.get("tema", "")
        return GetPromptResult(
            description=f"Datasets in {tema}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets en la categoría: {tema}

Pasos:
1. Usa search_open_data con theme="{tema}"
2. Lista los datasets encontrados
3. Agrupa por subtema si es posible
4. Muestra los más populares o actualizados""",
                    ),
                ),
            ],
        )

    elif name == "datasets_por_publicador":
        publicador = args.get("publicador", "")
        return GetPromptResult(
            description=f"Datasets from {publicador}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets publicados por: {publicador}

Pasos:
1. Usa list_open_data_publishers para encontrar el código del publicador
2. Usa search_open_data con publisher=<código>
3. Lista todos los datasets de ese publicador
4. Agrupa por categoría""",
                    ),
                ),
            ],
        )

    elif name == "datasets_por_formato":
        formato = args.get("formato", "CSV")
        return GetPromptResult(
            description=f"Datasets in {formato}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets disponibles en formato {formato}.

Pasos:
1. Usa search_open_data
2. Filtra los que tengan distribuciones en formato {formato}
3. Muestra los más relevantes con enlaces de descarga""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Analysis
    # =========================================================================
    elif name == "analizar_dataset":
        dataset_id = args.get("dataset_id", "")
        return GetPromptResult(
            description=f"Analyze {dataset_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza en detalle el dataset: {dataset_id}

Pasos:
1. Usa get_open_data_details con dataset_id="{dataset_id}"
2. Muestra toda la información:
   - Título y descripción completa
   - Publicador
   - Categorías y palabras clave
   - Cobertura temporal y geográfica
   - Frecuencia de actualización
   - Licencia
   - Todas las distribuciones con URLs
3. Evalúa la calidad del dataset:
   - ¿Está actualizado?
   - ¿Tiene formatos abiertos?
   - ¿Tiene metadatos completos?""",
                    ),
                ),
            ],
        )

    elif name == "formatos_dataset":
        dataset_id = args.get("dataset_id", "")
        return GetPromptResult(
            description=f"Formats for {dataset_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Lista los formatos disponibles para el dataset: {dataset_id}

Pasos:
1. Usa get_open_data_details con dataset_id="{dataset_id}"
2. Lista todas las distribuciones:
   - Formato (CSV, JSON, XML, etc.)
   - URL de descarga
   - Tamaño (si disponible)
3. Recomienda el mejor formato según el uso""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Thematic Searches
    # =========================================================================
    elif name == "datos_medio_ambiente":
        subtema = args.get("subtema")
        subtema_text = f" sobre {subtema}" if subtema else ""
        return GetPromptResult(
            description="Environmental data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets de medio ambiente{subtema_text}.

Pasos:
1. Usa search_open_data con theme="medio-ambiente"
2. Busca datasets de:
   - Calidad del aire
   - Calidad del agua
   - Residuos y reciclaje
   - Ruido ambiental
   - Espacios naturales
   - Emisiones
3. Muestra los más actualizados y completos""",
                    ),
                ),
            ],
        )

    elif name == "datos_transporte":
        tipo = args.get("tipo")
        tipo_text = f" de tipo {tipo}" if tipo else ""
        return GetPromptResult(
            description="Transport data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets de transporte y movilidad{tipo_text}.

Pasos:
1. Usa search_open_data con theme="transporte" o búsquedas específicas
2. Incluye:
   - Tráfico en tiempo real
   - Transporte público (horarios, paradas)
   - Bicicletas públicas
   - Aparcamientos
   - Accidentes de tráfico
3. Destaca los que tengan APIs o datos en tiempo real""",
                    ),
                ),
            ],
        )

    elif name == "datos_turismo":
        return GetPromptResult(
            description="Tourism data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de turismo.

Pasos:
1. Usa search_open_data con query="turismo"
2. Incluye:
   - Alojamientos
   - Puntos de interés
   - Rutas turísticas
   - Estadísticas de visitantes
   - Oficinas de turismo
3. Agrupa por ámbito geográfico""",
                    ),
                ),
            ],
        )

    elif name == "datos_economia":
        return GetPromptResult(
            description="Economic data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets económicos y empresariales.

Pasos:
1. Usa search_open_data con theme="economia"
2. Incluye:
   - Presupuestos públicos
   - Contratación pública
   - Actividad empresarial
   - Comercio
   - Empleo
3. Indica fuentes oficiales vs. derivadas""",
                    ),
                ),
            ],
        )

    elif name == "datos_salud":
        return GetPromptResult(
            description="Health data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de salud.

Pasos:
1. Usa search_open_data con theme="salud"
2. Incluye:
   - Centros sanitarios
   - Farmacias
   - Estadísticas sanitarias
   - Epidemiología
   - Listas de espera
3. Nota la sensibilidad de estos datos""",
                    ),
                ),
            ],
        )

    elif name == "datos_educacion":
        return GetPromptResult(
            description="Education data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de educación.

Pasos:
1. Usa search_open_data con theme="educacion"
2. Incluye:
   - Centros educativos
   - Universidades
   - Estadísticas de escolarización
   - Resultados PISA
   - Becas y ayudas
3. Agrupa por nivel educativo""",
                    ),
                ),
            ],
        )

    elif name == "datos_cultura":
        return GetPromptResult(
            description="Culture data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de cultura y patrimonio.

Pasos:
1. Usa search_open_data con query="cultura patrimonio"
2. Incluye:
   - Museos
   - Bibliotecas
   - Bienes de interés cultural
   - Eventos culturales
   - Archivos históricos
3. Destaca los datasets con datos georeferenciados""",
                    ),
                ),
            ],
        )

    elif name == "datos_urbanismo":
        return GetPromptResult(
            description="Urban planning data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de urbanismo y territorio.

Pasos:
1. Usa search_open_data con query="urbanismo cartografia"
2. Incluye:
   - Planeamiento urbanístico
   - Catastro
   - Callejeros
   - Cartografía
   - Infraestructuras
3. Indica formatos geoespaciales (Shapefile, GeoJSON, WMS)""",
                    ),
                ),
            ],
        )

    elif name == "datos_energia":
        return GetPromptResult(
            description="Energy data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de energía y suministros.

Pasos:
1. Usa search_open_data con query="energia electricidad"
2. Incluye:
   - Producción eléctrica
   - Consumo energético
   - Energías renovables
   - Precios de la electricidad
   - Puntos de recarga eléctrica
3. Destaca datos en tiempo real""",
                    ),
                ),
            ],
        )

    elif name == "datos_agricultura":
        return GetPromptResult(
            description="Agriculture data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de agricultura y medio rural.

Pasos:
1. Usa search_open_data con query="agricultura rural"
2. Incluye:
   - Cultivos y producción
   - Ganadería
   - Denominaciones de origen
   - Desarrollo rural
   - Regadíos
3. Fuentes del Ministerio de Agricultura""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # Geographic Searches
    # =========================================================================
    elif name == "datos_municipio":
        municipio = args.get("municipio", "")
        return GetPromptResult(
            description=f"Data from {municipio}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets del municipio de {municipio}.

Pasos:
1. Usa list_open_data_publishers para encontrar el ayuntamiento
2. Usa search_open_data con el código del publicador
3. También busca por nombre del municipio
4. Lista los datasets disponibles por categoría""",
                    ),
                ),
            ],
        )

    elif name == "datos_comunidad":
        comunidad = args.get("comunidad", "")
        return GetPromptResult(
            description=f"Data from {comunidad}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca datasets de la comunidad autónoma de {comunidad}.

Pasos:
1. Usa list_open_data_publishers para encontrar la CCAA
2. Usa search_open_data con el código del publicador
3. Lista los portales de datos propios si existen
4. Muestra los datasets más relevantes""",
                    ),
                ),
            ],
        )

    elif name == "datos_nacionales":
        return GetPromptResult(
            description="National data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets de la Administración General del Estado.

Pasos:
1. Usa list_open_data_publishers para identificar organismos estatales
2. Muestra los principales:
   - Ministerios
   - INE
   - AEMET
   - IGN
   - Otros organismos
3. Lista los datasets más importantes de cada uno""",
                    ),
                ),
            ],
        )

    # =========================================================================
    # API and Technical
    # =========================================================================
    elif name == "datasets_con_api":
        return GetPromptResult(
            description="Datasets with API",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets que ofrezcan acceso por API.

Pasos:
1. Usa search_open_data
2. Filtra los que tengan distribuciones de tipo API
3. Muestra:
   - Nombre del dataset
   - Tipo de API (REST, SPARQL, WMS, etc.)
   - Documentación
4. Destaca las APIs más útiles""",
                    ),
                ),
            ],
        )

    elif name == "datasets_tiempo_real":
        return GetPromptResult(
            description="Real-time datasets",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets con datos en tiempo real o actualizaciones frecuentes.

Pasos:
1. Usa search_open_data
2. Filtra por frecuencia de actualización
3. Categorías típicas:
   - Tráfico
   - Transporte público
   - Calidad del aire
   - Aparcamientos
   - Bicicletas públicas
4. Indica la frecuencia de actualización de cada uno""",
                    ),
                ),
            ],
        )

    elif name == "datos_geoespaciales":
        return GetPromptResult(
            description="Geospatial data",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca datasets geoespaciales/GIS.

Pasos:
1. Usa search_open_data con query="geoespacial cartografia"
2. Busca formatos:
   - Shapefile
   - GeoJSON
   - KML
   - WMS/WFS
3. Fuentes principales:
   - IGN (Instituto Geográfico Nacional)
   - Catastro
   - IDEE
4. Indica sistemas de coordenadas y cobertura""",
                    ),
                ),
            ],
        )

    else:
        raise ValueError(f"Unknown datos.gob.es prompt: {name}")
