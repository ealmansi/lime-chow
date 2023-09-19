const express = require("express");
const serverless = require("serverless-http");
const compareAsc = require('date-fns/compareAsc');
const format = require('date-fns/format');
const isBefore = require('date-fns/isBefore');
const parse = require('date-fns/parse');
const startOfDay = require('date-fns/startOfDay')
const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const { DynamoDBDocumentClient, ScanCommand } = require("@aws-sdk/lib-dynamodb");

/**
 * 
 */
function renderPage (events) {
  return (`
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Chow</title>
      <style>
        .events {
          list-style-type: none;
          padding-left: 10px;
        }
        h3 {
          margin-top: 30px;
          margin-bottom: 5px;
        }
        h2 {
          margin-top: 5px;
          max-width: 400px;
        }
        .event-thumbnail {
          margin-bottom: 10px;
          max-width: 400px;
        }
        .event-links {
          list-style-type: none;
          line-height: 20px;
          max-width: 400px;
          padding-left: 20px;
          font-family: monospace;
        }
      </style>
    </head>
    <body>
      ${renderEvents(events)}
    </body>
    </html>
  `);
}

function renderEvents (events) {
  return (`
    <ul class="events">
      ${events.map(renderEvent).join("\n")}
    </ul>
  `);
}

function renderEvent (event) {
  return (`
    <li id="${event.id}" class="event">
      ${renderEventHeader(event)}
      ${renderEventTitle(event)}
      ${renderEventThumbnail(event)}
      ${renderEventLinks(event.links)}
    </li>
  `);
}

function renderEventHeader (event) {
  const dayMonth = format(parse(event.date, "dd/MM/yy", new Date()), "dd.MM");
  const weekday = format(parse(event.date, "dd/MM/yy", new Date()), "EEEE");
  const venueMetadata = getVenueMetadata(event.venue);
  return (`
    <h3>
      ${[
        dayMonth,
        weekday,
        renderVenueLink(venueMetadata),
        venueMetadata.neighbourhood,
      ].join(" • ")}
    </h3>
  `);
}

function renderVenueLink (venueMetadata) {
  return (`
    <a
      href="${venueMetadata.link}"
      target="_blank"
      rel="noreferrer"
    >${venueMetadata.name}</a>
  `);
}

function getVenueMetadata (venue) {
  return {
    ["madame_claude"]: {
      name: "Madame Claude",
      neighbourhood: "Kreuzberg",
      link: "https://maps.app.goo.gl/9yoXrFGuJcKgoE928",
    },
    ["schokoladen"]: {
      name: "Schokoladen",
      neighbourhood: "Mitte",
      link: "https://maps.app.goo.gl/nfDnm9GVBjXv3bm37",
    },
    ["wild_at_heart"]: {
      name: "Wild at Heart",
      neighbourhood: "Kreuzberg",
      link: "https://maps.app.goo.gl/ZAaDdtSDabCuxbpn8",
    },
    ["peppi_guggenheim"]: {
      name: "Peppi Guggenheim",
      neighbourhood: "Neukölln",
      link: "https://maps.app.goo.gl/Kw3fqNnTjFdbYMu49",
    },
    ["loophole"]: {
      name: "Loophole",
      neighbourhood: "Neukölln",
      link: "https://maps.app.goo.gl/6Swi31q6NDWCdpQZ7",
    },
    ["arkaoda"]: {
      name: "Arkaoda",
      neighbourhood: "Neukölln",
      link: "https://maps.app.goo.gl/x4LVYefPDuPfSkBz7",
    },
    ["comedy_cafe_berlin"]: {
      name: "Comedy Café Berlin",
      neighbourhood: "Neukölln",
      link: "https://maps.app.goo.gl/LyxvV46EjAeecmiq7",
    },
    ["clash"]: {
      name: "Clash",
      neighbourhood: "Kreuzberg",
      link: "https://maps.app.goo.gl/hQHUap2MsdWXDFdp7",
    },
    ["sameheads"]: {
      name: "Sameheads",
      neighbourhood: "Neukölln",
      link: "https://maps.app.goo.gl/9L4RMbxraSQ6jkyL8",
    },
  }[venue];
}

function renderEventTitle (event) {
  return (`
      <h2>
        <a href="${event.url}" target="_blank" rel="noreferrer">
          ${event.title}
        </a>
      </h2>
  `);
}

function renderEventThumbnail (event) {
  return (`
    <img
      class="event-thumbnail"
      src="${event.thumbnail_url}"
      alt="${event.title}"
    />
  `);
}

function renderEventLinks (links) {
  const topLinks = links
    .slice()
    .sort(compareEventLinks)
    .slice(0, 4);
  return (`
    <ul class="event-links">
      ${topLinks.map(renderEventLink).join("\n")}
    </ul>
  `);
}

function renderEventLink (link) {
  const maxLength = 50;
  const linkDisplay =
    link.length > maxLength
      ? `${link.slice(0, maxLength - '...'.length)}...`
      : link;
  return (`
    <li>
      <a href="${link}" target="_blank" rel="noreferrer">
        ${linkDisplay}
      </a>
    </li>
  `);
}

function compareEventLinks (link1, link2) {
  return getEventLinkPriority(link1) - getEventLinkPriority(link2);
}

function getEventLinkPriority (link) {
  const priorities = [
    [100, link => link.includes("linktr.ee")],
    [100, link => link.includes("bandcamp.com")],
    [100, link => link.includes("soundcloud.com")],
    [100, link => link.includes("mixcloud.com")],
    [100, link => link.includes("spotify.com")],
    [200, link => link.includes("youtube.com")],
    [300, link => link.includes("instagram.com")],
    [1000, link => link.includes("facebook.com/events")],
    [400, link => link.includes("facebook.com")],
    [900, () => true],
  ];
  for (const [priority, matcher] of priorities) {
    if (matcher(link)) {
      return priority;
    }
  }
}

/**
 * 
 */
async function getEvents (documentClient) {
  const { Items: events } = await documentClient.send(
    new ScanCommand({
      TableName: "events",
    }),
  );
  return events.sort(compareEvents).filter(isUpcoming);
}

function compareEvents (event1, event2) {
  if (event1.id === event2.id) {
    return 0;
  }
  if (event1.date === event2.date) {
    return event1.id.localeCompare(event2.id);
  }
  const date1 = parse(event1.date, "dd/MM/yy", new Date());
  const date2 = parse(event2.date, "dd/MM/yy", new Date());
  return compareAsc(date1, date2);
}

function isUpcoming (event) {
  const date = parse(event.date, "dd/MM/yy", new Date());
  return !isBefore(startOfDay(date), startOfDay(new Date()));
}

/**
 * 
 */
function buildApp () {
  const documentClient = DynamoDBDocumentClient.from(
    new DynamoDBClient(),
  );
  const app = express();
  app.use(express.json());
  app.get("/", async function (_req, res) {
    const events = await getEvents(documentClient);
    res.send(renderPage(events));
  });
  app.use((_req, res, _next) => {
    res.sendStatus(404);
  });
  return app;
}

/**
 * 
 */
module.exports.handler = serverless(buildApp());
