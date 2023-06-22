<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes"/>

  <xsl:template match="/">
    <html>
      <head>
        <title>KanjiDic2</title>
      </head>
      <body>
        <h1>KanjiDic2</h1>
        <table>
          <tr>
            <th>Kanji</th>
            <th>Reading</th>
            <th>Meaning</th>
            <th>Stroke Count</th>
          </tr>
          <xsl:apply-templates select="kanjidic2/character"/>
        </table>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="character">
    <tr>
      <td><xsl:value-of select="literal"/></td>
      <td><xsl:value-of select="reading_meaning/rmgroup/reading[@r_type='ja_on']"/></td>
      <td><xsl:value-of select="reading_meaning/rmgroup/meaning"/></td>
      <td><xsl:value-of select="misc/stroke_count"/></td>
    </tr>
  </xsl:template>
</xsl:stylesheet>