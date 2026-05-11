MOTIVOS_RECLAMO = {
    "Faltante de mercadería": {
        "Con Nota de Crédito": ["rto", "sku", "dpc", "nc"],
        "Reposición (Remito Manual)": ["rto_manual", "sku"]
    },
    "Sobrantes": {
        "Con devolución": ["rto", "sku", "or_number", "dpc", "nc"],
        "Sin devolución": ["rto", "sku", "fc"]
    },
    "Roturas": {
        "Por transporte tercerizado": ["rto", "nic", "sku", "or_number", "reclamo_cds", "dpc", "nc"],
        "En armado": ["rto", "nic", "sku", "or_number", "dpc", "nc"],
        "En entrega local": ["rto", "sku", "or_number", "dpc", "nc"]
    },
    "Status de pedidos": {
        "Con remito": ["rta", "pdf"],
        "Sin remito": ["rta"]
    },
    "Reclamos al transporte": {
        "Demoras": ["reclamo"],
        "Faltantes de bultos": ["reclamo", "seguimiento", "siniestro_dev"],
        "Perdidas Parciales o totales": ["reclamo", "seguimiento", "siniestro_dev"],
        "Cruces de remitos": ["reclamo", "seguimiento", "siniestro_dev"],
        "Entregas no correspondientes a cliente": ["reclamo", "seguimiento"]
    },
    "Devoluciones": {
        "Próximos a Vencer": ["or_number", "dpc", "nc"],
        "Error EAN": ["rto", "or_number", "dpc", "nc"],
        "No pedidos a comercial": ["rto", "or_number", "dpc", "nc"],
        "Sobre stock": ["rto", "or_number", "dpc", "nc"],
        "Sobrantes": ["rto", "or_number", "dpc"],
        "Roturas/ daños": ["rto", "nic", "or_number", "reclamo", "dpc", "nc"],
        "Mal estado, Ingresos a CC": ["rto", "or_number", "dpc", "nc"]
    },
    "Por solicitud": {
        "NC": ["resolucion_solicitud"],
        "FC": ["fc"],
        "RTO": ["rto"],
        "Documentación a CDS": ["doc_cds"],
        "Conformes": ["resolucion_solicitud"]
    }
}

# Define field labels for UI
FIELD_LABELS = {
    "rto": "Remito (RTO)",
    "rto_manual": "Remito Manual (Reposición)",
    "sku": "Artículos (SKU)",
    "dpc": "Ingreso Devolución (DPC/DT)",
    "nc": "Nota de Crédito (NC)",
    "or_number": "Orden de Retiro (OR)",
    "fc": "Factura (FC)",
    "nic": "Nro Logística CDS (NIC)",
    "rto_manual": "Remito Manual",
    "reclamo_cds": "Reclamo CDS",
    "rta": "Respuesta (RTA)",
    "pdf": "Adjunto / PDF",
    "reclamo": "Nro de Reclamo",
    "seguimiento": "Seguimiento",
    "siniestro_dev": "Siniestro / Devolución",
    "resolucion_solicitud": "Resolución / Archivo PDF",
    "doc_cds": "Documentación CDS"
}

# Define areas responsible for timestamps (used for dashboard metrics)
AREA_RESPONSIBILITY = {
    "or_number": "Tráfico",
    "nic": "Tráfico",
    "dpc": "Depósito/Devoluciones",
    "nc": "Facturación",
    "fc": "Facturación"
}
