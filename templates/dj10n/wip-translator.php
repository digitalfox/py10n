<?php
// Auteur:   {{ name }}
$page_title = "Traduction en français des applications de KDE";
$site_root = "./";
include_once ("functions.inc");
include "header.inc";
$site_title = "KDE en français";
$site_external = true;
$showedit = false;
$name="{{ name }}";
$mail="{{ mail|safe }}";
?>
<p>Pour toutes demandes de travaux, adressez vos courriers électroniques à
<a href="mailto:{{ mail|safe }}">{{ name }}</a>.</p>
<div id="sommaire"><h3>Sommaire</h3>
       <ul><li>
               <a href="apps.php">
               <img src="../img/package.png" alt="Affectation" />
               Applications classées par module
               </a>
       </li><li>
               <a href="translators.php">
               <img src="../img/affectation.png" alt="Affectation" />
               Traductions affectées par traducteur
               </a>
       </li><li>
               <a href="stats.php">
               <img src="../img/stats.png" alt="Affectation" />
               Statistiques de traduction
               </a>
       </li></ul></div><hr />

<table class="packages"><tr>
{% for translator in translators %}
    {% cycle '' '' '' '</tr><tr>' %}
    <td><a href='#{{ translator.email }}'>{{ translator.firstname }} {{ translator.lastname }}</a></td>
{% endfor %}
</tr></table><hr />


<h3 id=''><span class='Applications orphelines'>Applications orphelines</span></h3>
<table class="poFiles"><thead><tr>
    <th class="nom">Fichier à traduire</th>
    <th class="bookingDate">Date d'affectation</th>
    <th class="traduire" title="Nombre de messages déjà traduits."><a href='#legend'>À traduire</a></th>
    <th class="actualiser" title="Nombre de messages non traduits."><a href='#legend'>À mettre à jour</a></th>
    <th class="pology" title="Nombre de messages dont le message origine ou le contexte a changé."><a href='#legend'>À  vérifier</a></th>
    <th class="effectuer" title="Nombre de messages comportants des erreurs selon l'outil « Pology »."><a href='#legend'>Traduits</a></th>
</tr></thead>
<tbody>
{% for po in orphan_pos %}
    <tr class="{% cycle 'odd' 'even' %} {{ po.getCss }}">
    <th><a href='{{ po.webPath }}'>{{ po.name }}</a></th>
    <td class='bookingDate'>{{ po.startdate|default_if_none:"-"}}</td>
    <td>{{ po.untranslated }}</td>
    <td>{{ po.fuzzy }}</td>
    <td class="pology"><a href='../pology-errors.php?po={{ po.name }}.po&amp;package={{ module.name }}&amp;branch={{ branch.path }}&amp;mode=gui'>{{ po.error }}
    {% ifequal po.error 0 %}<img src='../img/status/ok.png' alt='Aucune erreur' />
    {% else %}<img src='../img/status/warning.png' alt='Erreurs Pology' /> {% endifequal %}</a></td>
    <td>{{ po.translated }}</td>
    </tr>            
{% endfor %}
</tbody>
<tfoot>
<tr><td>Totaux</td><td>&nbsp;</td><td>3070</td><td>86</td><td class='pology'>746</td><td>10743</td></tr></tfoot>
</table><hr />

{% for translator, translator_values in translators.items %}
    <h3 id='{{ translator.email }}'><span class='{{ translator.firstname }} {{ translator.lastname }}'>{{ translator.firstname }} {{ translator.lastname }}</span></h3>
    <table class="poFiles"><thead><tr>
        <th class="nom">Nom</th>
        <th class="bookingDate">Date d'affectation</th>
        <th class="traduire" title="Nombre de messages non traduits."><a href='#legend'>À traduire</a></th>
        <th class="actualiser" title="Nombre de messages dont le message origine ou le contexte a changé."><a href='#legend'>À mettre à jour</a></th>
        <th class="pology" title="Nombre de messages comportants des erreurs selon l'outil « Pology »."><a href='#legend'>À vérifier</a></th>
        <th class="effectuer" title="Nombre de messages déjà traduits."><a href='#legend'>Traduits</a></th>
    </tr></thead>    
    {% for po in translator_values.pos %}
        <tr class="{% cycle 'odd' 'even' %} {{ po.getCss }}">
        <th><a href='{{ po.webPath }}'>{{ po.name }}</a></th>
        <td class='bookingDate'>{{ po.startdate|date:"j b y"}}</td>
        <td>{{ po.untranslated }}</td>
        <td>{{ po.fuzzy }}</td>
        <td class="pology"><a href='../pology-errors.php?po={{ po.name }}.po&amp;package={{ module.name }}&amp;branch={{ branch.path }}&amp;mode=gui'>{{ po.errortho }}
        {% ifequal po.errortho 0 %}<img src='../img/status/ok.png' alt='Aucune erreur' />
        {% else %}<img src='../img/status/warning.png' alt='Erreurs Pology' /> {% endifequal %}</a></td>
        <td>{{ po.translated }}</td>
        </tr>
    {% endfor %}
    </tbody><tfoot>
    <tr><td>Totaux</td>
    <td>&nbsp;</td>
    <td>{{ translator_values.untranslated }}</td>
    <td>{{ translator_values.fuzzy }}</td>
    <td class='pology'>{{ translator_values.error }}</td>
    <td>{{ translator_values.translated }}</td>
    </tr></tfoot></table><hr />
{% endfor %}

<div id="legend">
                   <h3>Légende</h3>
                   <ul>
                   <li><strong>Traduits :</strong> Nombre de messages déjà traduits.</li>
                   <li><strong>À traduire :</strong> Nombre de messages non traduits.</li>
                   <li><strong>À mettre à jour :</strong> Nombre de messages dont le message origine ou le contexte a changé.</li>
                   <li><strong>À vérifier :</strong> Nombre de messages comportants des erreurs selon l'outil « Pology ».</li>
                   </ul>
                   <h3>Couleurs</h3>
                   <ul>
                   <li><strong class="translated">fichier.po</strong> : Fichier intégralement traduit et sans erreur.</li>
                   <li><strong class="translated hasPologyErrors">fichier.po</strong> : Fichier intégralement traduit, mais comportant des erreurs Pology.</li>
                   <li><strong class="partial">fichier.po</strong> : Fichier partiellement traduit, et contenant éventuellement des erreurs Pology.</li>
                   <li><strong class="untranslated">fichier.po</strong> : Aucune chaîne de caractères traduite.</li>
                   </ul>
                   </div>
                   
        <div id="lastUpdate">Dernière mise à jour : {{ now|date:"l j F Y, G:i:s" }}</div><?php
            include "footer.inc";
            ?>
            