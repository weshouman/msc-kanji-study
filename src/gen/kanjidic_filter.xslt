<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
    
    <xsl:template match="/">
        <kanjidic2>
            <xsl:apply-templates select="kanjidic2/character[position() &lt;= 100]"/>
        </kanjidic2>
    </xsl:template>
    
    <xsl:template match="character">
        <xsl:copy-of select="."/>
    </xsl:template>
    
</xsl:stylesheet>