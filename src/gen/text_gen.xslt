<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" indent="no"/>

  <xsl:template match="/">
    <xsl:apply-templates select="library"/>
  </xsl:template>
  
  <xsl:template match="library">
    <xsl:for-each select="book">
      <xsl:value-of select="concat(position(), ': Book &quot;', title, '&quot; authored by ', author, ' on ', year)"/>
      <xsl:text>&#xa;</xsl:text>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
