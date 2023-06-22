<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <head>
        <title>Library Catalog</title>
      </head>
      <body>
        <h1>Library Catalog</h1>
        <xsl:apply-templates select="library"/>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="library">
    <table>
      <tr>
        <th>Title</th>
        <th>Author</th>
        <th>Year</th>
      </tr>
      <xsl:apply-templates select="book"/>
    </table>
  </xsl:template>
  
  <xsl:template match="book">
    <tr>
      <td><xsl:value-of select="title"/></td>
      <td><xsl:value-of select="author"/></td>
      <td><xsl:value-of select="year"/></td>
    </tr>
  </xsl:template>
</xsl:stylesheet>