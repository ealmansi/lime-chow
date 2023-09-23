const express = require("express");
const serverless = require("serverless-http");
const parseISO = require("date-fns/parseISO");
const compareAsc = require("date-fns/compareAsc");
const format = require("date-fns/format");
const isBefore = require("date-fns/isBefore");
const startOfDay = require("date-fns/startOfDay");
const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
const {
  DynamoDBDocumentClient,
  ScanCommand,
} = require("@aws-sdk/lib-dynamodb");

/**
 *
 */
function renderPage(events) {
  return `
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Chow</title>
      <style>
        html, body {
          width: 100%;
          margin: 0px;
          padding: 0px;
          font-family: sans-serif;
        }
        .events {
          width: min(380px, 100% - 20px);
          margin: 0px 0px 20px 0px;
          padding: 10px;
          list-style-type: none;
        }
        .event {
          width: 100%;
          margin: 0px 0px 30px 0px;
          padding: 0px;
        }
        .event-info {
          width: 100%;
          margin: 0px 0px 5px 0px;
          padding: 0px;
        }
        .event-title {
          width: 100%;
          margin: 0px 0px 10px 0px;
          padding: 0px;
        }
        .event-thumbnail {
          width: 100%;
          margin: 0px 0px 10px 0px;
          padding: 0px;
          text-align: center;
          background: #ffd7ef;
        }
        .event-thumbnail img {
          max-width: 100%;
          max-height: 500px;
        }
        .event-links {
          width: 100%;
          margin: 0px;
          padding: 0px;
          list-style-type: none;
          line-height: 20px;
          font-family: monospace;
        }
      </style>
    </head>
    <body>
      ${or(() => renderEvents(events), "Something went wrong.")}
    </body>
    </html>
  `;
}

function renderEvents(events) {
  return `
    <ul class="events">
      ${events
        .map((event) => or(() => renderEvent(event), undefined))
        .filter((html) => html !== undefined)
        .join("<hr />")}
    </ul>
  `;
}

function renderEvent(event) {
  return `
    <li id="${event.id}" class="event">
      ${renderEventInfo(event)}
      ${renderEventTitle(event)}
      ${or(() => renderEventThumbnail(event), "")}
      ${or(() => renderEventLinks(event), "")}
    </li>
  `;
}

function renderEventInfo(event) {
  const datetime = event.starts_at
    ? parseISO(event.starts_at)
    : parseISO(event.starts_on);
  const date = format(datetime, "dd.MM");
  const weekday = format(datetime, "EEEE");
  const intl = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Berlin",
    hour: "numeric",
  });
  const time = event.starts_at
    ? intl.format(datetime).toLowerCase().replace(" ", "")
    : undefined;
  const venueMetadata = getVenueMetadata(event.venue);
  return `
    <h3 class="event-info">
      <em>${[
        date,
        time ? `${weekday} ${time}` : weekday,
        renderVenueLink(venueMetadata),
        venueMetadata.neighbourhood,
      ].join(" • ")}</em>
    </h3>
  `;
}

function renderVenueLink(venueMetadata) {
  return `
    <a
      href="${venueMetadata.link}"
      target="_blank"
      rel="noreferrer"
    >${venueMetadata.name}</a>
  `;
}

function renderEventTitle(event) {
  return `
      <h2 class="event-title">
        <a href="${event.url}" target="_blank" rel="noreferrer">
          ${event.title}
        </a>
      </h2>
  `;
}

function renderEventThumbnail(event) {
  return `
    <div class="event-thumbnail">
      <img
        src="${event.thumbnail_url}"
        alt="${event.title}"
        loading="lazy"
      />
    </div>
  `;
}

function renderEventLinks(event) {
  const topLinks = event.links.slice().sort(compareEventLinks).slice(0, 4);
  return `
    <ul class="event-links">
      ${topLinks.map(renderEventLink).join("\n")}
    </ul>
  `;
}

function renderEventLink(link) {
  const maxLength = 50;
  const linkDisplay =
    link.length > maxLength
      ? `${link.slice(0, maxLength - "...".length)}...`
      : link;
  return `
    <li>
      <a href="${link}" target="_blank" rel="noreferrer">
        ${linkDisplay}
      </a>
    </li>
  `;
}

function compareEventLinks(link1, link2) {
  return getEventLinkPriority(link1) - getEventLinkPriority(link2);
}

function getEventLinkPriority(link) {
  const priorities = [
    [100, (link) => link.includes("linktr.ee")],
    [100, (link) => link.includes("bandcamp.com")],
    [100, (link) => link.includes("soundcloud.com")],
    [100, (link) => link.includes("mixcloud.com")],
    [100, (link) => link.includes("spotify.com")],
    [200, (link) => link.includes("youtube.com")],
    [300, (link) => link.includes("instagram.com")],
    [1000, (link) => link.includes("facebook.com/events")],
    [400, (link) => link.includes("facebook.com")],
    [900, () => true],
  ];
  for (const [priority, matcher] of priorities) {
    if (matcher(link)) {
      return priority;
    }
  }
}

function getVenueMetadata(venue) {
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

function or(thunk, value) {
  try {
    return thunk();
  } catch (err) {
    console.error(err);
    return value;
  }
}

/**
 *
 */
async function getEvents(documentClient) {
  const { Items: events } = await documentClient.send(
    new ScanCommand({
      TableName: "events",
    }),
  );
  return events.sort(compareEvents).filter(isUpcoming);
}

function compareEvents(event1, event2) {
  const datetime1 = event1.starts_at
    ? parseISO(event1.starts_at)
    : parseISO(event1.starts_on);
  const datetime2 = event2.starts_at
    ? parseISO(event2.starts_at)
    : parseISO(event2.starts_on);
  const compareResult = compareAsc(datetime1, datetime2);
  if (compareResult !== 0) {
    return compareResult;
  }
  return event1.id.localeCompare(event2.id);
}

function isUpcoming(event) {
  const date = parseISO(event.starts_on);
  return !isBefore(date, startOfDay(new Date()));
}

/**
 *
 */
function buildApp() {
  const documentClient = DynamoDBDocumentClient.from(new DynamoDBClient());
  const app = express();
  app.use(express.json());
  app.get("/", async function (_req, res) {
    const events = await getEvents(documentClient);
    res.send(renderPage(events));
  });
  app.get("/api", async function (_req, res) {
    const events = await getEvents(documentClient);
    res.send(events);
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
